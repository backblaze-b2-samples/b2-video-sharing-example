from django.contrib.auth import views as auth_views
from django.urls import path

from mysite.core import views

urlpatterns = [
    # Website
    path('', views.DocumentListView.as_view(), name='home'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('upload/', views.DocumentCreateView.as_view(), name='upload'),
    path('videos/delete_all', views.delete_all),
    path('videos/<str:document_detail>', views.DocumentDetailView.as_view(), name='watch'),

    # REST API
    path('videos/', views.transcoder_notification, name='notification'),
    path('documents/<str:name>', views.document_detail, name='document_detail'),
]
