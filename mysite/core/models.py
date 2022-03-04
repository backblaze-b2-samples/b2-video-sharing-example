from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from mysite.storage_backends import PrivateMediaStorage


class Document(models.Model):
    title = models.CharField(max_length = 256)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    upload = models.FileField(storage=PrivateMediaStorage())
    transcoded = models.FileField(storage=PrivateMediaStorage(), default=None, blank=True, null=True)
    user = models.ForeignKey(User, related_name='documents', on_delete=models.CASCADE)


class Video(models.Model):
    status = models.CharField(max_length = 16)
    inputObject = models.CharField(max_length = 1024)
    outputObject = models.CharField(max_length = 1024)