from django.http import JsonResponse
from django.shortcuts import render

from notifications.views import send_sys_notification
from super_admin.models import Complain
from videos.models import Video


# Create your views here.

def get_review_video(request):
    if request.method=='GET':
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
def review_video(request):
    if request.method=='POST':
        video_id=request.POST.get('video_id')
        res=request.POST.get('res')
        reason=request.POST.get('reason')
        try:
            video=Video.objects.get(video_id=video_id)
            user_id=video.user_id
            if res==0 :#审核不通过
                try :#判断是否被投诉过
                    complain=Complain.objects.filter(video_id=video_id)
                    for c in complain:
                        if c.is_message_sent==0:
                            send_sys_notification('系统',c.user_id,f"你投诉视频名称为f'{video.title}',已成功，平台已下架该视频")
                            c.is_message_sent=1
                            c.status=1
                            c.save()
                    video.delete()
                except Complain.DoesNotExist:
                    pass
                send_sys_notification('系统',video.user_id,"审核不通过")
            else:
                video.reviewed_status=res
                video.save()
                try :#判断是否被投诉过
                    complain=Complain.objects.filter(video_id=video_id)
                    for c in complain:
                        if c.is_message_sent==0:
                            send_sys_notification('系统',c.user_id,f"你投诉视频名称为f'{video.title}'失败，平台平台未察觉到相关因素")
                            c.is_message_sent=1
                            c.status=1
                            c.save()
                except Complain.DoesNotExist:
                    pass
                send_sys_notification('系统', video.user_id, "审核通过")
                return JsonResponse({'errno': 0, 'msg': "审核通过！"})
        except Video.DoesNotExist:
            return JsonResponse({'errno': 0, 'msg': "视频不存在！"})
    else:
        return JsonResponse({'errno': 0, 'msg': "请求方法错误！"})
def review_complaint_video(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        video_id = request.POST.get('video_id')
        op=request.POST.get('op')
        try:
            video=Video.objects.get(id=video_id)
            if op=='重审':
                video.reviewed_status=0
                video.save()
            elif op=='删除':
                video.delete()
            else :
                return JsonResponse({'errno': 0, 'msg': "操作错误！"})
        except Video.DoesNotExist:
            return JsonResponse({'errno': 0, 'msg': "视频不存在！"})
    else:
        return JsonResponse({'errno': 0, 'msg': "请求方法错误！"})


def get_complaint_video_(request):
    if request.method == 'GET':
        try:
            complains=Complain.objects.filter(status=0)
            video_list=[]
            for c in complains:
                video_id=c.video_id
                try:
                    video=Video.objects.get(video_id)
                    video_list.append(video.to_simple_dict())
                except:
                    pass
        except Complain.DoesNotExist:
            return JsonResponse({'errno': 0, 'msg': "没有投诉视频！"})
    else:
        return JsonResponse({'errno': 0, 'msg': "请求方法错误！"})


