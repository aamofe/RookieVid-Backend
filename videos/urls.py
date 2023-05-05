from django.urls import path
from .views import *

urlpatterns=[
    path('upload_video',upload_video),
    path('manage_video',manage_video),
    path('get_video_by_label',get_video_by_label),
    path('get_hot_video',get_hot_video),
]