from django.urls import path
from .views import *

urlpatterns = [
    path('sendvcode', send_mail_vcode),
    path('validatevacode', validate_mail_vcode),
    path('rigister', register),
    path('login', login),
    path('logout', logout),
]