import secrets

from django.contrib.auth.models import User
from django.db import models

from cattube.storage_backends import PrivateMediaStorage


def generate_transcoder_token():
    return secrets.token_urlsafe(32)


class Video(models.Model):
    title = models.CharField(max_length=256)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    raw = models.FileField(storage=PrivateMediaStorage())
    transcoded = models.FileField(storage=PrivateMediaStorage(), default=None, blank=True, null=True)
    thumbnail = models.FileField(storage=PrivateMediaStorage(), default=None, blank=True, null=True)
    transcoder_token = models.CharField(max_length=128, default=generate_transcoder_token, editable=False)
    user = models.ForeignKey(User, related_name='videos', on_delete=models.CASCADE)

    def __str__(self):
        return f'"{self.title}", uploaded at {self.uploaded_at}, upload {self.raw}, transcoded {self.transcoded}, user {self.user.username}'


class Notification(models.Model):
    status = models.CharField(max_length=16)
    inputObject = models.CharField(max_length=1024)
    outputObject = models.CharField(max_length=1024)
    thumbnail = models.CharField(max_length=1024)
