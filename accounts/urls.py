from django.urls import path
from .views import *

urlpatterns = [
    path('send_vcode', send_vcode),
    # path('validatevacode', validate_mail_vcode),
    path('register', register),
    path('login', login),
    path('logout', logout),
    path('unsubscribe', unsubscribe),
    path('display_myprofile', display_myprofile),
    path('display_profile', display_profile),
    path('edit_profile', edit_profile),
    path('edit_avatar', edit_avatar),
    path('change_password', change_password),
    path('change_email', change_email),
    path('create_follow', create_follow),
    path('remove_follow', remove_follow),
    path('get_followings', get_followings),
    path('get_followers', get_followers),
    path('get_videos', get_videos),
    path('get_favorite', get_favorite),
    path('get_favlist', get_favlist),
    path('delete_favorite', delete_favorite),
    path('delete_favorite_video', delete_favorite_video),
]