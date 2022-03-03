from django.urls import path
from django.contrib.auth import views as auth_views

from mysite.core import views


urlpatterns = [
    path('', views.DocumentCreateView.as_view(), name='home'),
]
