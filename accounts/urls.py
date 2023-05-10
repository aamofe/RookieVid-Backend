from django.urls import path
from .views import *

urlpatterns = [
    path('sendvcode', send_mail_vcode),
    # path('validatevacode', validate_mail_vcode),
    path('register', register),
    path('login', login),
    path('logout', logout),
    path('display_profile', display_profile),
    path('edit_profile', edit_profile),
    path('change_password', change_password),
    path('change_email', change_email),
    path('create_follow', create_follow),
    path('remove_follow', remove_follow),
    path('get_followings', get_followings),
    path('get_followers', get_followers),
]