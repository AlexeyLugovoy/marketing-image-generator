from django.urls import path
from .views import register_user, login_user, get_username

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('username/', get_username, name='get_username')
]
