from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decorator.decorator_permission import validate_login, validate_all
from notifications.models import Notification
from accounts.models import User


# Create your views here.

@csrf_exempt
@validate_login
# 管理端给用户发送通知
def send_notification(request):
    if request.method == 'POST':
        send_to = request.POST.get("send_to")
        content = request.POST.get("content")
        send_from = request.user.username
        new_notification = Notification(send_from=send_from, send_to=send_to, content=content)
        new_notification.save()
        return JsonResponse({'errno': 0, 'msg': "通知发送成功"})
    else:
        return JsonResponse({'error': 0, 'msg': "请求方式错误"})


# 发送系统通知
def send_sys_notification(send_from, send_to, content):
    if User.objects.filter(id=send_to).exists():
        new_notification = Notification(send_from=send_from, send_to=send_to, content=content)
        new_notification.save()
        return True
    else:
        return False


def check_notification(request):
    if request.method == 'GET':

        return JsonResponse({'errno': 0, 'msg': "通知发送成功"})
    else:
        return JsonResponse({'error': 0, 'msg': "请求方式错误"})
