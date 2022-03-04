from rest_framework import serializers
from .models import Video, Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['title', 'uploaded_at', 'upload', 'transcoded', 'user']


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['status', 'inputObject', 'outputObject']