from django.http import JsonResponse
from django.shortcuts import render

from notifications.views import send_sys_notification
from super_admin.models import Complain
from videos.models import Video
import datetime

# Create your views here.
from decorator.decorator_permission import validate_login, validate_all
@validate_login
def get_review_video(request):
    if request.method=='GET':
        user=request.user
        if user.status!=1:
            return JsonResponse({'errno': 0, 'msg': "没有管理员权限！"})
        video = Video.objects.filter(reviewed_status=0)
        video_list=[]
        for v in video:
            video_list.append(v.to_dict())
        if len(video_list)==0:
            return JsonResponse({'errno': 0, 'msg': "审核完啦！"})
        else:
            return JsonResponse({'errno': 0, 'video':video_list,'msg': "继续审核喔"})
    else:
        return JsonResponse({'errno': 0, 'msg': "请求方法错误！"})
@validate_login    
def review_video(request):
    if request.method=='POST':
        user=request.user
        if user.status!=1:
            return JsonResponse({'errno': 0, 'msg': "没有管理员权限！"})
        video_id=request.POST.get('video_id')
        res=request.POST.get('res')
        reason=request.POST.get('reason')
        try:
            video=Video.objects.get(id=video_id)
            user_id=video.user_id
            if len(res)==0:
                return JsonResponse({'errno': 0, 'msg': "审核结果不能为空！"})
            if res==0 :#审核不通过
                try :#判断是否被投诉过
                    complain=Complain.objects.filter(video_id=video_id)
                    for c in complain:
                        if c.is_message_sent==0:
                            send_sys_notification('管理员',c.user_id,f"你投诉视频名称为f'{video.title}',已成功，平台已下架该视频")
                            c.is_message_sent=1
                            c.status=1
                            c.save()
                    video.delete()
                except Complain.DoesNotExist:
                    pass
                send_sys_notification('管理员',video.user_id,"审核不通过")
            else:
                video.reviewed_status=res
                video.reviewed_at=datetime.datetime.now()
                video.save()
                try :#判断是否被投诉过
                    complain=Complain.objects.filter(video_id=video_id)
                    for c in complain:
                        if c.is_message_sent==0:
                            send_sys_notification('管理员',c.user_id,f"你投诉视频名称为f'{video.title}'失败，平台平台未察觉到相关因素")
                            c.is_message_sent=1
                            c.status=1
                            c.save()
                except Complain.DoesNotExist:
                    pass
                send_sys_notification('管理员', video.user_id, "审核通过")
                return JsonResponse({'errno': 0, 'msg': "审核通过！"})
        except Video.DoesNotExist:
            return JsonResponse({'errno': 0, 'msg': "视频不存在！"})
    else:
        return JsonResponse({'errno': 0, 'msg': "请求方法错误！"})

@validate_login
def review_complain_video(request):
    if request.method == 'POST':
        user=request.user
        if user.status!=1:
            return JsonResponse({'errno': 0, 'msg': "没有管理员权限！"})
        video_id = request.POST.get('video_id')
        op=request.POST.get('op')
        try:
            video=Video.objects.get(id=video_id)
            if op=='review':
                video.reviewed_status=0
                video.save()
                return JsonResponse({'errno': 0, 'msg': "视频已进入重审队列！"})
            elif op=='delete':
                video.delete()
                #发消息
                return JsonResponse({'errno': 0, 'msg': "视频已删除！"})
            else :
                return JsonResponse({'errno': 0, 'msg': "操作错误！"})
        except Video.DoesNotExist:
            return JsonResponse({'errno': 0, 'msg': "视频不存在！"})
    else:
        return JsonResponse({'errno': 0, 'msg': "请求方法错误！"})

@validate_login
def get_complain_video(request):
    if request.method == 'GET':
        user=request.user
        if user.status!=1:
            return JsonResponse({'errno': 0, 'msg': "没有管理员权限！"})
        try:
            complains=Complain.objects.filter(status=0)
            video_list=[]
            for c in complains:
                video_id=c.video_id
                #print("111",video_id)
                try:
                    video=Video.objects.get(id=video_id)
                    #print('2222',video.id)
                    #这里需要判断被投诉视频是否已经在video_list里面
                    v=video.to_simple_dict()
                    if not v in video_list:
                        video_list.append(v)
                except:
                    pass
            return JsonResponse({'errno': 0, 'video':video_list,'msg': "获取投诉视频成功！"})
        except Complain.DoesNotExist:
            return JsonResponse({'errno': 0, 'msg': "没有投诉视频！"})
    else:
        return JsonResponse({'errno': 0, 'msg': "请求方法错误！"})


