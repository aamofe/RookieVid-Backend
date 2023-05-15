from django.urls import path
from .views import *

urlpatterns=[
    path('upload_video',upload_video),
    path('manage_video',manage_video),
    path('get_video_by_label',get_video_by_label),
    path('get_video_by_hotness',get_video_by_hotness),
    path('search_video',search_video),
    path('view_video',view_video),
    path('comment_video',comment_video),
    path('reply_comment',reply_comment),
    path('like_video',like_video),
    path('create_favorite',create_favorite),
    path('favorite_video',favorite_video),
    path('get_favorite',get_favorite),
]