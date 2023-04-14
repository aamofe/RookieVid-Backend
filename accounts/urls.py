from django.urls import path
from .views import *

urlpatterns = [
    path('sendvcode', send_mail_vcode),
    path('validatevacode', validate_mail_vcode),
    path('register', register),
    path('login', login),
    path('logout', logout),
]