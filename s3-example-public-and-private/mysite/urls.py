from django.urls import path
from django.contrib.auth import views as auth_views

from mysite.core import views


urlpatterns = [
    path('', views.DocumentCreateView.as_view(), name='home'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.PrivateDocumentCreateView.as_view(), name='profile'),
]

