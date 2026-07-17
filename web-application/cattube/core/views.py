import hmac
import os
import posixpath

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Video
from .serializers import VideoSerializer, NotificationSerializer

transcoder_url = settings.TRANSCODER_WEBHOOK
private_media_location = settings.B2_PRIVATE_MEDIA_LOCATION


def private_object_key(name):
    return f'{private_media_location}/{name}'


def private_media_name(object_key):
    prefix = f'{private_media_location}/'
    if not object_key.startswith(prefix):
        raise ValueError(f'object key must start with {prefix}')

    name = object_key[len(prefix):]
    normalized_name = posixpath.normpath(name)
    if normalized_name in ('', '.') or normalized_name.startswith('../') or '/..' in normalized_name:
        raise ValueError('object key must stay inside the private media prefix')

    return normalized_name


def expected_output_names(raw_name):
    stem = os.path.splitext(raw_name)[0]
    return f'{stem}.mp4', f'{stem}.jpg'


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
        send_notification_to_transcoder(
            webhook,
            private_object_key(self.object.raw.name),
            self.object.transcoder_token,
        )
        return response


@login_required
def delete_all_videos(request):
    print('Deleting all the videos!')
    Video.objects.all().delete()
    return HttpResponseRedirect(reverse('home'))


# JavaScript polls this endpoint - we don't want the browser to cache the response!
@never_cache
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


def send_notification_to_transcoder(webhook, object_key, token):
    payload = {
        'inputObject': object_key,
        'webhook': webhook,
        'token': token
    }
    print(f'Sending transcoder job for {object_key} to {transcoder_url}')
    r = requests.post(transcoder_url, json=payload)
    print(f'Status code: {r.status_code}')


@api_view(['POST'])
def receive_notification_from_transcoder(request):
    serializer = NotificationSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        print(f'Received notification for {data["inputObject"]}')

        try:
            raw = private_media_name(data['inputObject'])
            transcoded = private_media_name(data['outputObject'])
            thumbnail = private_media_name(data['thumbnail'])
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        print(f'Getting {raw}')

        try:
            doc = Video.objects.get(raw=raw)
        except Video.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not hmac.compare_digest(data['token'], doc.transcoder_token):
            return Response({'detail': 'invalid transcoder token'}, status=status.HTTP_403_FORBIDDEN)

        expected_transcoded, expected_thumbnail = expected_output_names(raw)
        if transcoded != expected_transcoded or thumbnail != expected_thumbnail:
            return Response({'detail': 'unexpected transcoder output key'}, status=status.HTTP_400_BAD_REQUEST)

        doc.transcoded.name = transcoded
        doc.thumbnail.name = thumbnail

        print(f'Saving {doc}')
        doc.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
