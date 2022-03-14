from django.contrib.auth.models import User
from django.db import models

from catblaze.storage_backends import PrivateMediaStorage


class Video(models.Model):
    title = models.CharField(max_length=256)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    raw = models.FileField(storage=PrivateMediaStorage())
    transcoded = models.FileField(storage=PrivateMediaStorage(), default=None, blank=True, null=True)
    thumbnail = models.FileField(storage=PrivateMediaStorage(), default=None, blank=True, null=True)
    user = models.ForeignKey(User, related_name='videos', on_delete=models.CASCADE)

    def __str__(self):
        return f'"{self.title}", uploaded at {self.uploaded_at}, upload {self.raw}, transcoded {self.transcoded}, user {self.user.username}'


class Notification(models.Model):
    status = models.CharField(max_length=16)
    inputObject = models.CharField(max_length=1024)
    outputObject = models.CharField(max_length=1024)
    thumbnail = models.CharField(max_length=1024)
