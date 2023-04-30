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


def create_remote_directory(host, port, username, password, remote_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, port=port, username=username, password=password)
    sftp = client.open_sftp()
    try:
        # 尝试打开文件夹，如果文件夹不存在则会抛出 IOError 异常
        sftp.stat(remote_path)
    except IOError:
        # 文件夹不存在，创建文件夹
        sftp.mkdir(remote_path)
    sftp.close()
    client.close()


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

        # 判断标签是否有效
        if label not in LABELS:
            return JsonResponse({'success': False, 'error': 'Invalid label'})

        # 将视频和封面文件上传到云服务器
        video_storage = SFTPStorage(host='101.43.159.45', username='aamofe', password='aamofe12@')
        cover_storage = SFTPStorage(host='101.43.159.45', username='aamofe', password='aamofe12@')
        video_count = Video.objects.filter(label=label).count()

        # 拼接视频和封面文件的路径
        video_id = video_count + 1
        video_path = f'/home/aamofe/data/video_file/{label}/{video_id}.mp4'
        cover_path = f'/home/aamofe/data/video_cover/{label}/{video_id}.png'
        create_remote_directory(host='101.43.159.45', port=3306, username='aamofe', password='aamofe12@',
                                remote_path=f'/home/aamofe/data/video_file/{label}/')
        create_remote_directory(host='101.43.159.45', port=3306, username='aamofe', password='aamofe12@',
                                remote_path=f'/home/aamofe/data/video_cover/{label}/')
        video_storage.upload(video_file.temporary_file_path(), video_path)
        cover_storage.upload(cover_file.temporary_file_path(), cover_path)

        video_storage.close()
        cover_storage.close()

        # 将视频信息保存到数据库
        video = Video.objects.create(
            label=LABELS.index(label),
            title=title,
            description=description,
            video_path=video_path,
            cover_path=cover_path,
            created_at=datetime.datetime.now()
        )
        video.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})
