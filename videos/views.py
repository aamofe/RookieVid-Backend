import datetime
import os
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from storages.backends.sftpstorage import SFTPStorage
from django.db.models import Q, Count, Count, F, ExpressionWrapper
import videos
from django.db import models
from RookieVid_Backend import settings
from django.db.models import Max
import paramiko
from django.core import serializers
from accounts.models import User
from videos.models import Video, Like, Comment, Reply, Collect

from random import sample

# 视频分类标签
LABELS = ['娱乐', '军事', '生活', '音乐', '学习', '科技', '运动', '游戏', '影视', '美食']

def get_video_by_label(request):
    if request.method == 'GET' :
        label=request.GET.get('label')
        if label not in LABELS:
            return JsonResponse({'errno': 2011, 'msg': "标签错误！"})
        videos = Video.objects.filter(label=label)
        random_videos = sample(list(videos), min(10,sum(videos)))
        video_list = []
        for video in random_videos:
            video_dict =video.to_dict()
            print("video_url : ",video_dict.get('url'))
            video_list.append(video_dict)

        return JsonResponse({'errno': 0, 'msg': "返回成功！", 'videos': video_list}, safe=False)
    else:
        return JsonResponse({'errno': 2001, 'msg': "请求方法错误！"})
    

def get_video_by_hotness(request):
    if request.method == 'GET':
        # 构建热度计算表达式
        hotness_expression = ExpressionWrapper(
            Count('like_amount') + F('view_amount') * 0.5,
            output_field=models.FloatField()
        )
        # 获取符合条件的视频，并按热度计算排序
        videos = Video.objects.filter(reviewed_status=1).annotate(
            hotness_score=hotness_expression
        ).order_by('-hotness_score', '-like_amount', '-view_amount', 'id')
        # 获取前6个视频
        videos = videos[:6]
        #print("数量 : ",)
        video_list = []
        for video in videos:
            video_dict = video.to_dict()
            #print("video_url: ", video_dict.get('video_url'))
            video_list.append(video_dict)

        return JsonResponse({'errno': 0, 'msg': "返回成功！", 'videos': video_list}, safe=False)
    else:
        return JsonResponse({'errno': 2001, 'msg': "请求方法错误！"})

    
@csrf_exempt
def upload_video(request):
    if request.method == 'POST':
        # 获取上传的视频和封面文件
        user_id=1
        video_file = request.FILES.get('video_file')
        cover_file = request.FILES.get('cover_file')
        label = request.POST.get('label')
        title = request.POST.get('title')
        description = request.POST.get('description')
        #print('video_file : ',video_file,'label : ',label)
        # 将视频信息保存到数据库
        video = Video.objects.create(
            label=label,
            title=title,
            description=description,
            user_id=user_id,
            created_at=datetime.datetime.now()
        )
        video_path = os.path.join(settings.VIDRO_URL, f'{video.id}.mp4')
        cover_path = os.path.join(settings.COVER_URL, f'{video.id}.png')
        video.video_path=video_path
        video.cover_path=cover_path

        with open(video_path, 'wb+') as f:
            for chunk in video_file.chunks():
                f.write(chunk)
                
        with open(cover_path, 'wb+') as f:
            for chunk in cover_file.chunks():
                f.write(chunk)
        video.save()
        return JsonResponse({'errno': 0, 'msg': "上传成功"})
    else:
        return JsonResponse({'errno': 2001, 'msg': "请求方法错误！"})

def manage_video(request):
    if request.method == 'GET':
        # 获取操作类型和视频ID
        op = request.GET.get('op')
        video_id = request.GET.get('video_id')

        if op == 'delete':
            try:
                # 根据视频ID从数据库中删除该视频记录
                video = Video.objects.get(id=video_id)
                video.delete()
                return JsonResponse({'errno': 0, 'msg': '删除成功'})
            except Video.DoesNotExist:
                return JsonResponse({'errno': 2004, 'msg': '视频不存在'})
        else:
            return JsonResponse({'errno': 2005, 'msg': '操作不合法'})
    else:
        return JsonResponse({'errno': 2001, 'msg': '请求方法不合法'})

def search_video(request):
    if request.method=='GET':
        keyword = request.GET.get('keyword')
        if not keyword:
            return JsonResponse({'errno': 2006, 'msg': '关键字不能为空'})
        # 使用 Q 对象进行模糊查询
        query = Q(title__icontains=keyword) | Q(description__icontains=keyword)
        videos = Video.objects.filter(query)
        serialized_videos = serializers.serialize('json', videos, fields=('id','title', 'description', 'cover_path','video_path','view_amount','like'))
        # 将字典列表作为JSON响应返回
        return JsonResponse({'errno': 0, 'msg': "返回成功！", 'videos': serialized_videos}, safe=False)
    else:
        return JsonResponse({'errno': 2002, 'msg': "请求方法错误！"})

def view_video(request):
    if request.method=='GET':
        #这里可能需要把 不只是根据id获取视频，还有其他方式
        video_id=request.GET.get('video_id')
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return JsonResponse({'errno': 2004, 'msg': '视频不存在'})
        serialized_videos = serializers.serialize('json',[video] , fields=('id','title', 'description', 'cover_path','video_path','view_amount','like'))
        # 将字典列表作为JSON响应返回
        return JsonResponse({'errno': 0, 'msg': "返回成功！", 'videos': serialized_videos}, safe=False)
    else:
        return JsonResponse({'errno': 2001, 'msg': "请求方法错误！"})

@csrf_exempt
def comment_video(request):
    if request.method == 'POST':
        try :
            user_id = request.session['id']
        except:
            user_id=1 #测试用！！！
            #return JsonResponse({'errno': 2003, 'msg': "未登录！"})
        video_id = request.POST.get('video_id')
        content = request.POST.get('content')
        created_at = datetime.now()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'errno': 2007, 'msg': '用户不存在'})
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return JsonResponse({'errno': 2004, 'msg': '视频不存在'})
        comment = Comment.objects.create(
            user=user,
            video=video,
            content=content,
            created_at=created_at
        )
        comment.save()
        return JsonResponse({'errno': 0, 'msg': '评论成功'})
    else:
        return JsonResponse({'errno': 2001, 'msg': "请求方法错误！"})

@csrf_exempt
def reply_comment(request):
    if request.method == 'POST':
        # 获取请求中传入的参数
        user_id = request.POST.get('user_id')
        comment_id = request.POST.get('comment_id')
        content = request.POST.get('content')
            # 创建回复评论对象
        reply = Reply(user_id=user_id, comment_id=comment_id, content=content)
        reply.save()
        # 构造返回给前端的数据
        return JsonResponse({'errno': 0, 'errmsg': 'success'})
    else:
        return JsonResponse({'errno': 2001, 'msg': "请求方法错误！"})

@csrf_exempt
def like_video(request):
    if request.method == 'POST':
        # 获取请求中传入的参数
        user_id = request.POST.get('user_id')
        video_id = request.POST.get('video_id')

        # 检查该用户是否已经点赞过该视频
        try:
            like = Like.objects.get(user_id=user_id, video_id=video_id)
            # 用户已经点赞过该视频，则取消点赞
            like.delete()
            data = {'status': 'success', 'action': 'cancel'}
        except Like.DoesNotExist:
            # 用户没有点赞过该视频，则添加点赞记录
            like = Like(user_id=user_id, video_id=video_id)
            like.save()
            data = {'status': 'success', 'action': 'like'}
    else:
        return JsonResponse({'errno': 2001, 'msg': "请求方法错误！"})

