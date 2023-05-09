from django.urls import path
from .views import *

urlpatterns=[
    path("review_video",review_video),
]