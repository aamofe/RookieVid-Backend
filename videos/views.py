import datetime
import os
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from storages.backends.sftpstorage import SFTPStorage

import videos
from RookieVid_Backend import settings

import paramiko

from videos.models import Video


# 视频分类标签
LABELS = ['娱乐', '军事', '生活', '音乐', '学习', '科技', '运动', '游戏', '影视', '美食']


@csrf_exempt
def upload_video(request):
    if request.method == 'POST':
        # 获取上传的视频和封面文件
        video_file = request.FILES.get('video_file')
        cover_file = request.FILES.get('cover_file')
        label = request.POST.get('label')
        title = request.POST.get('title')
        description = request.POST.get('description')
        video_count = Video.objects.all().count()
        video_id = video_count + 1
        # 将视频和封面文件上传到云服务器
        video_storage = SFTPStorage()
        cover_storage = SFTPStorage()
        video_storage.location = 'data/video_file/'
        cover_storage.location = 'data/video_cover/'
        print("video_storage : ",video_storage)
        print("cover_storage_storage : ",cover_storage)
        print("video_storage.location : ",video_storage.location)
        print("cover_storage.location : ",cover_storage.location)
        #save() 方法的参数是 Django 的 File 对象
        #upload() 方法的参数是本地文件路径
        video_path = video_storage.save(f'{video_id}_{title}.mp4', video_file)
        cover_path = cover_storage.save(f'{video_id}_{title}.png', cover_file)
        print("video_path : ",video_path)
        print("cover_path : ",cover_path)
        video_storage.close()
        cover_storage.close()

        # 将视频信息保存到数据库
        video = Video.objects.create(
            id=video_id,
            label=LABELS.index(label),
            title=title,
            description=description,
            video_path=video_path,
            cover_path=cover_path,
            created_at=datetime.datetime.now()
        )
        video.save()

        return JsonResponse({'errno': 0, 'msg': "上传成功"})

    return JsonResponse({'errno': 2001, 'msg': "请求方法不合法"})

@csrf_exempt
def manage_video(request):
    if request.method=='GET':
        #目前只考虑删除稿件
        op=request.GET.get('操作')

