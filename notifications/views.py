from django.shortcuts import render
from django.http import JsonResponse
from notifications.models import Notification
from accounts.models import User

# Create your views here.

# 管理端给用户发送通知
def send_notification(request):
    if request.method == 'POST':
        send_to = request.POST.get("send_to")
        content = request.POST.get("content")
        send_from = request.user.uid
        new_notification = Notification(send_from=send_from, send_to=send_to, content=content)
        new_notification.save()
        return JsonResponse({'errno': 0, 'msg': "通知发送成功"})
    else:
        return JsonResponse({'error': 1, 'msg': "请求方式错误"})

def send_sys_notification(send_to, send_from, content):
    if User.objects.filter(uid=send_to).exists():
        new_notification = Notification(send_from=send_from, send_to=send_to, content=content)
        new_notification.save()
        return True
    else:
        return False

def check_notification(request):
    if request.method == 'GET':

        return JsonResponse({'errno': 0, 'msg': "通知发送成功"})
    else:
        return JsonResponse({'error': 1, 'msg': "请求方式错误"})