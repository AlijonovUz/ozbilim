from django.urls import path

from .views import *

urlpatterns = [
    # Auth routes
    path('auth/login/', LoginPageView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),

    # Profile route
    path('settings/', UserSettingsView.as_view(), name='settings'),
    path('<str:username>/', ProfileView.as_view(), name='profile'),
]
