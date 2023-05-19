from django.urls import path
from .views import *

urlpatterns=[
    path("review_video",review_video),
    path("get_review_video",get_review_video),
    path("review_complain_video",review_complain_video),
    path("get_complain_video",get_complain_video)
]