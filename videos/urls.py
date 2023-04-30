from django.urls import path
from .views import *

urlpatterns=[
    path('upload_video',upload_video)
]