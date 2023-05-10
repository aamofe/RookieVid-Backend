from django.shortcuts import render

from videos.models import Video


# Create your views here.


def review_video(request):
    if request.method=='POST':
        video_id=request.POST.get('vodeo_id')
        video=Video.objects.filter(video_id=video_id)
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

