from django.urls import path
from .views import *

urlpatterns=[
    path('video_upload',video_upload)
]