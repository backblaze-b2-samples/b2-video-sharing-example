from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Document, Video
from .serializers import DocumentSerializer, VideoSerializer

import requests


transcoder_url = settings.TRANSCODER_WEBHOOK
private_bucket_name = settings.AWS_PRIVATE_MEDIA_LOCATION


def index(request):
    return render(request, 'core/index.html')


@method_decorator(login_required, name='dispatch')
class DocumentListView(ListView):
    model = Document


@method_decorator(login_required, name='dispatch')
class DocumentDetailView(DetailView):
    model = Document
    slug_field = 'upload'
    slug_url_kwarg = 'document_detail'

@method_decorator(login_required, name='dispatch')
class DocumentCreateView(CreateView):
    model = Document
    fields = ['title', 'upload', ]

    def get_success_url(self):
        return reverse_lazy('watch', kwargs={'document_detail' : self.object.upload.name})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        response = super().form_valid(form)
        webhook = self.request.build_absolute_uri(reverse('notification'))
        print(f'Our webhook is {webhook}')
        notify_transcoder(webhook, f'{private_bucket_name}/{self.object.upload.name}')
        return response


@login_required
def delete_all(request):
    response = Document.objects.all().delete()
    print(response)
    return HttpResponseRedirect(reverse('myvideos'))


@api_view(['GET'])
def document_detail(request, name):
    print(f'Received request: {name}')

    try:
        doc = Document.objects.get(upload=name)
        serializer = DocumentSerializer(doc)
        return Response(serializer.data)
    except Document.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


def notify_transcoder(webhook, object_key):
    payload = {
        'inputObject': object_key,
        'webhook': webhook
    }
    print(f'Sending {payload} to {transcoder_url}')
    r = requests.post(transcoder_url, json=payload)
    print(f'Status code: {r.status_code}')


@api_view(['POST'])
def transcoder_notification(request):
    serializer = VideoSerializer(data=request.data)
    if serializer.is_valid():
        print(f'Received notification: {serializer.data}')

        try:
            # Remove the path prefixes from the object keys
            upload = request.data['inputObject'].removeprefix(f'{private_bucket_name}/')
            transcoded = request.data['outputObject'].removeprefix(f'{private_bucket_name}/')

            print(f'Getting doc {upload}')

            doc = Document.objects.get(upload=upload)
            doc.transcoded.name = transcoded

            print(f'Saving {doc}')
            doc.save()
        except Document.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
