from django.urls import path
from .views import *

urlpatterns = [
    path('send_notification', send_notification),
    path('count_unread', count_unread),
    path('get_all_notification', get_all_notification),
    path('check_notification', check_notification),
    path('read_all', read_all),
    path('delete_notification', delete_notification),
]