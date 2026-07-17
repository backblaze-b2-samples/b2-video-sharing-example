from rest_framework import serializers

from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['title', 'uploaded_at', 'raw', 'transcoded', 'thumbnail', 'user']


class NotificationSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=16)
    inputObject = serializers.CharField(max_length=1024)
    outputObject = serializers.CharField(max_length=1024)
    thumbnail = serializers.CharField(max_length=1024)
    token = serializers.CharField(max_length=128)
