import datetime
import os
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from storages.backends.sftpstorage import SFTPStorage
from django.db.models import Q
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
        print('video_file:', video_file.name)
        print('cover_file:', cover_file.name)
        print('label:', label)
        print('title:', title)
        print('description:', description)
        
        # # 将视频和封面文件上传到云服务器
        # video_storage = SFTPStorage()
        # cover_storage = SFTPStorage()
        # video_storage.location = 'data/video_file/'
        # cover_storage.location = 'data/video_cover/'
        # print("video_storage : ",video_storage)
        # print("cover_storage_storage : ",cover_storage)
        # print("video_storage.location : ",video_storage.location)
        # print("cover_storage.location : ",cover_storage.location)
        # #save() 方法的参数是 Django 的 File 对象
        # #upload() 方法的参数是本地文件路径
        # video_path = video_storage.save(f'{video_id}_{title}.mp4', video_file)
        # cover_path = cover_storage.save(f'{video_id}_{title}.png', cover_file)
        # print("video_path : ",video_path)
        # print("cover_path : ",cover_path)
        # video_storage.close()
        # cover_storage.close()

        video_path = os.path.join(settings.VIDRO_URL, f'{video_id}_{title}.mp4')
        cover_path = os.path.join(settings.COVER_URL, f'{video_id}_{title}.mp4')

        with open(video_path, 'wb+') as f:
            for chunk in video_file.chunks():
                f.write(chunk)
                
        with open(cover_path, 'wb+') as f:
            for chunk in cover_file.chunks():
                f.write(chunk)
        try:
            user_id = request.session['id']
        except:
            user_id = 0

        # 将视频信息保存到数据库
        video = Video.objects.create(
            label=LABELS.index(label),
            title=title,
            description=description,
            video_path=video_path,
            cover_path=cover_path,
            user_id=user_id,
            created_at=datetime.datetime.now()
        )
        video.save()

        return JsonResponse({'errno': 0, 'msg': "上传成功"})

    return JsonResponse({'errno': 2001, 'msg': "请求方法不合法"})

@csrf_exempt
def manage_video(request):
    if request.method == 'GET':
        # 获取操作类型和视频ID
        op = request.GET.get('操作')
        video_id = request.GET.get('视频ID')

        if op == 'delete':
            try:
                # 根据视频ID从数据库中删除该视频记录
                video = Video.objects.get(id=video_id)
                video.delete()
                return JsonResponse({'errno': 0, 'msg': '删除成功'})
            except Video.DoesNotExist:
                return JsonResponse({'errno': 4001, 'msg': '视频不存在'})
        else:
            return JsonResponse({'errno': 4002, 'msg': '操作不合法'})

    else:
        return JsonResponse({'errno': 2001, 'msg': '请求方法不合法'})

def search_video(request):
    keyword = request.GET.get('keyword')

    if not keyword:
        return JsonResponse({'errno': 4001, 'msg': '关键字不能为空'})

    # 使用 Q 对象进行模糊查询
    query = Q(title__icontains=keyword) | Q(description__icontains=keyword)
    videos = Video.objects.filter(query)

    # 构造返回的视频列表数据
    video_list = []
    for video in videos:
        video_data = {
            'id': video.id,
            'title': video.title,
            'description': video.description,
            'cover_url': video.get_cover_url(),
        }
        video_list.append(video_data)

    return JsonResponse({'errno': 0, 'msg': '查询成功', 'data': video_list})

def play_video(request, video_id):
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        return JsonResponse({'error': '视频不存在'})
    
    response_data = {
        'id': video.id,
        'title': video.title,
        'description': video.description,
        'cover_url': video.cover_path.url,
        'video_url': video.video_path.url,
    }
    
    return JsonResponse(response_data)

@csrf_exempt
def comment_video(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        video_id = request.POST.get('video_id')
        content = request.POST.get('content')
        created_at = datetime.now()
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'errno': 4001, 'msg': '无效的用户ID'})
        
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return JsonResponse({'errno': 4002, 'msg': '无效的视频ID'})
        
        comment = Comment.objects.create(
            user=user,
            video=video,
            content=content,
            created_at=created_at
        )
        
        return JsonResponse({'errno': 0, 'msg': '评论成功'})
    
    return JsonResponse({'errno': 2001, 'msg': '请求方法不合法'})

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
        response_data = {'errno': 0, 'errmsg': 'success'}
        return JsonResponse(response_data)

@csrf_exempt
def likes_video(request):
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
        
        return JsonResponse(data)

@csrf_exempt
def collect_video(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        video_id = request.POST.get('video_id')
        try:
        # 检查用户是否已经收藏该视频
            existed_collect = Collect.objects.get(user_id=user_id, video_id=video_id)
            # 如果已经收藏，删除收藏
            existed_collect.delete()
            data = {'status': 'success', 'msg': '取消收藏成功'}
            return JsonResponse(data)
        except Collect.DoesNotExist:
        # 如果未收藏，创建收藏
            collect = Collect(user_id=user_id, video_id=video_id)
            collect.save()
            data = {'status': 'success', 'msg': '收藏成功'}
            return JsonResponse(data)
    else:
        data = {'errno': 2001, 'msg': '请求方法不合法'}
        return JsonResponse(data)