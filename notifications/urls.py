from django.urls import path
from .views import *

urlpatterns = [
    path('send_notification', send_notification),
]