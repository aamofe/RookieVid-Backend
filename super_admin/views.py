from django.http import JsonResponse
from django.shortcuts import render

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

        review_status=request.POST.get('review_status')
        reason=request.POST.get('reason')
        try:
            video=Video.objects.get(video_id=video_id)
            user_id=video.user_id
            if review_status==0:#审核不通过
                #发送消息到user
                user_id=1#乱写的，防止乱码
            else:
                video.reviewed_status=review_status
                return JsonResponse({'errno': 0, 'msg': "审核通过！"})
        except Video.DoesNotExist:
            return JsonResponse({'errno': 0, 'msg': "视频不存在！"})
def review_complaint_video(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        video_id = request.POST.get('video_id')
def get_review_video_list(request):
    if request.method == 'GET':
        return 0


def get_complaint_video_list(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        video_id = request.POST.get('video_id')

def send_notification(request):#这里的工程量很大，目测
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        video_id = request.POST.get('video_id')

