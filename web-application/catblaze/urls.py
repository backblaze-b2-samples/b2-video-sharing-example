from django.contrib.auth import views as auth_views
from django.urls import path

from catblaze.core import views

urlpatterns = [
    # Website
    path('', views.VideoListView.as_view(), name='home'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('upload/', views.VideoCreateView.as_view(), name='upload'),
    path('videos/delete_all', views.delete_all_videos),
    path('videos/<str:video_detail>', views.VideoDetailView.as_view(), name='watch'),

    # REST API
    path('api/videos/', views.receive_notification_from_transcoder, name='notification'),
    path('api/videos/<str:name>', views.video_detail, name='video_detail'),
]
