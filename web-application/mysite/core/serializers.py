from rest_framework import serializers

from .models import Notification, Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['title', 'uploaded_at', 'upload', 'transcoded', 'thumbnail', 'user']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['status', 'inputObject', 'outputObject', 'thumbnail']
