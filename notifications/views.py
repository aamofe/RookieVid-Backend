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
        send_to = request.POST.getlist('send_to')
        title = request.POST.get('title')
        content = request.POST.get('content')
        if request.user.status != 1:
            return JsonResponse({'errno': 1, 'msg': "没有管理员权限"})
        for user_id in send_to:
            new_notification = Notification(send_from=0, send_to=user_id, title=title, content=content, link_type=0,
                                            link_id=0)
            new_notification.save()
        return JsonResponse({'errno': 0, 'msg': "通知发送成功"})
    else:
        return JsonResponse({'error': 1, 'msg': "请求方式错误"})


# 发送系统通知
def send_sys_notification(send_from, send_to, title, content, link_type, link_id):
    if User.objects.filter(id=send_to).exists():
        new_notification = Notification(send_from=send_from, send_to=send_to, title=title, content=content,
                                        link_type=link_type, link_id=link_id)
        new_notification.save()
        return True
    else:
        return False


@csrf_exempt
@validate_login
def count_unread(request):
    if request.method == 'GET':
        user = request.user
        count = 0
        try:
            count = Notification.objects.filter(send_to=user.id, is_read=False).count()
            return JsonResponse({'errno': 0, 'msg': "查询未读消息成功", 'count': count})
        except Notification.DoesNotExist:
            return JsonResponse({'errno': 0, 'msg': "暂无新消息", 'count': count})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})


def get_all_method(user_id):
    unread_list = []
    read_list = []
    count_unread = 0
    count_all = 0
    try:
        notifications = Notification.objects.filter(send_to=user_id)
        for notification in notifications:
            context_1 = notification.to_dict()

            if int(notification.send_from) == 0:
                context_2 = {
                    'user_id': 0,
                    'username': '管理员',
                    'avatar_url': 'https://aamofe-1315620690.cos.ap-beijing.myqcloud.com/avatar_file/super_admin.png',
                    'signature': ''
                }
            elif User.objects.filter(id=notification.send_from):
                send_user = User.objects.get(id=notification.send_from)
                context_2 = send_user.to_simple_dict()
                context_2['user_id'] = context_2.pop('id', None)
            else:
                context_2 = {
                    'user_id': -1,
                    'username': '用户已注销',
                    'avatar_url': 'https://aamofe-1315620690.cos.ap-beijing.myqcloud.com/avatar_file/default.png',
                    'signature': ''
                }
            context = {k: v for context in [context_1, context_2] for k, v in context.items()}
            if not notification.is_read:
                unread_list.append(context)
                count_unread += 1
            else:
                read_list.append(context)
            count_all += 1
        resp = {'errno': 0, 'msg': "消息列表查询成功", 'count_all': count_all, 'count_unread': count_unread,
                'unread_list': unread_list, 'read_list': read_list}
        return resp
    except Notification.DoesNotExist:
        return {'errno': 0, 'msg': "消息列表为空", 'data': []}


@csrf_exempt
@validate_login
def get_all_notification(request):
    if request.method == 'GET':
        user = request.user
        resp = get_all_method(user.id)
        return JsonResponse(resp)
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})


@csrf_exempt
@validate_login
def check_notification(request):
    if request.method == 'GET':
        user = request.user
        notification_id = request.GET.get('notification_id')
        try:
            notification = Notification.objects.get(id=notification_id)
            if int(notification.send_to) != user.id:
                return JsonResponse({'errno': 1, 'msg': "没有操作权限"})
            notification.is_read = True
            notification.save()
            return JsonResponse({'errno': 0, 'msg': "消息查看成功", 'data': notification.to_dict()})
        except Notification.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': "消息已删除或不存在"})
    else:
        return JsonResponse({'error': 1, 'msg': "请求方式错误"})


@csrf_exempt
@validate_login
def read_all(request):
    if request.method == 'POST':
        user = request.user
        try:
            notifications = Notification.objects.filter(send_to=user.id)
            for notification in notifications:
                notification.is_read = True
                notification.save()
            return JsonResponse({'errno': 0, 'msg': "消息全部设为已读"})
        except Notification.DoesNotExist:
            return JsonResponse({'errno': 0, 'msg': "消息列表为空"})
    else:
        return JsonResponse({'error': 1, 'msg': "请求方式错误"})


@csrf_exempt
@validate_login
def delete_notification(request):
    if request.method == 'POST':
        delete = request.POST.getlist('delete_id')
        user = request.user
        try:
            for notification_id in delete:
                notification = Notification.objects.get(id=notification_id)
                if int(notification.send_to) != user.id:
                    return JsonResponse({'errno': 1, 'msg': "没有操作权限"})
                notification.delete()
            return JsonResponse({'errno': 0, 'msg': "消息删除成功"})
        except Notification.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': "消息已删除或不存在"})
    else:
        return JsonResponse({'error': 1, 'msg': "请求方式错误"})
