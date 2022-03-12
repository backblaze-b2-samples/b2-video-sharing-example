import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Video
from .serializers import VideoSerializer, NotificationSerializer

transcoder_url = settings.TRANSCODER_WEBHOOK
private_bucket_name = settings.AWS_PRIVATE_MEDIA_LOCATION


class VideoListView(ListView):
    model = Video

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        videos = Video.objects.all()
        context['videos'] = videos
        return context


class VideoDetailView(DetailView):
    model = Video
    slug_field = 'raw'
    slug_url_kwarg = 'video_detail'


@method_decorator(login_required, name='dispatch')
class VideoCreateView(CreateView):
    model = Video
    fields = ['title', 'raw', ]

    def get_success_url(self):
        return reverse_lazy('watch', kwargs={'video_detail': self.object.raw.name})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        response = super().form_valid(form)
        webhook = self.request.build_absolute_uri(reverse('notification'))
        print(f'Our webhook is {webhook}')
        send_notification_to_transcoder(webhook, f'{private_bucket_name}/{self.object.raw.name}')
        return response


@login_required
def delete_all_videos(request):
    print('Deleting all the videos!')
    Video.objects.all().delete()
    return HttpResponseRedirect(reverse('home'))


@api_view(['GET'])
def video_detail(request, name):
    print(f'Received request for detail on: {name}')

    try:
        doc = Video.objects.get(raw=name)
        serializer = VideoSerializer(doc)
        print(f'Returning : {serializer.data}')
        return Response(serializer.data)
    except Video.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


def send_notification_to_transcoder(webhook, object_key):
    payload = {
        'inputObject': object_key,
        'webhook': webhook
    }
    print(f'Sending {payload} to {transcoder_url}')
    r = requests.post(transcoder_url, json=payload)
    print(f'Status code: {r.status_code}')


@api_view(['POST'])
def receive_notification_from_transcoder(request):
    serializer = NotificationSerializer(data=request.data)
    if serializer.is_valid():
        print(f'Received notification: {serializer.data}')

        try:
            # Remove the path prefixes from the object keys
            raw = request.data['inputObject'].removeprefix(f'{private_bucket_name}/')
            transcoded = request.data['outputObject'].removeprefix(f'{private_bucket_name}/')
            thumbnail = request.data['thumbnail'].removeprefix(f'{private_bucket_name}/')

            print(f'Getting {raw}')

            doc = Video.objects.get(raw=raw)
            doc.transcoded.name = transcoded
            doc.thumbnail.name = thumbnail

            print(f'Saving {doc}')
            doc.save()
        except Video.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
