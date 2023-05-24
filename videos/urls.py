from django.urls import path
from .views import *

urlpatterns=[
    path('upload_video',upload_video),
    path('delete_video',delete_video),
    path('update_video',update_video),
    path('get_video_by_label',get_video_by_label),
    path('get_video_by_hotness',get_video_by_hotness),
    path('search',search),
    path('view_video',view_video),
    path('comment_video',comment_video),
    path('reply_comment',reply_comment),
    path('like_video',like_video),
    path('create_favorite',create_favorite),
    path('favorite_video',favorite_video),
    path('get_favorite',get_favorite),
    path('delete_comment',delete_comment),
    path('delete_reply',delete_reply),
    path('get_related_video',get_related_video),
    path('get_video',get_video),
    path('complain_video',complain_video),
    path('is_complaint',is_complaint),
    path('get_comment',get_comment),
    path('call_back',call_back),
    path('get_video_by_view_amount',get_video_by_view_amount),
    path('get_one_video',get_one_video),
    #path('test',test),
]