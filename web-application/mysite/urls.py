from django.urls import path
from django.contrib.auth import views as auth_views

from mysite.core import views


urlpatterns = [
    # Website
    path('', views.index, name='home'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('myvideos/', views.DocumentListView.as_view(), name='myvideos'),
    path('myvideos/upload/', views.DocumentCreateView.as_view(), name='upload'),
    path('myvideos/delete_all', views.delete_all),
    path('myvideos/<str:document_detail>', views.DocumentDetailView.as_view(), name='watch'),

    # REST API
    path('videos/', views.transcoder_notification, name='notification'),
    path('documents/<str:name>', views.document_detail, name='document_detail'),
]
