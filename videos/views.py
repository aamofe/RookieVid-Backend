import datetime
import uuid

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q, Count, F, ExpressionWrapper
from django.db import models
from django.core import serializers
import datetime
from accounts.models import User
from videos.cos_utils import get_cos_client
from videos.models import Video, Like, Comment, Reply, Favorite, Favlist
from random import sample
from django.contrib.auth.models import AnonymousUser
# 视频分类标签
LABELS = ['娱乐', '军事', '生活', '音乐', '学习', '科技', '运动', '游戏', '影视', '美食']

def get_video_by_label(request):
    if request.method == 'GET':
        label = request.GET.get('label')
        num=int(request.GET.get('num'))
        if label not in LABELS:
            return JsonResponse({'errno': 0, 'msg': "标签错误！"})
        videos = Video.objects.filter(label=label,reviewed_status=1)
        if num==-1:
            num=len(videos)
        #print('num : ',num)
        random_videos = sample(list(videos), num)
        video_list = []
        for video in random_videos:
            video_dict = video.to_dict()
            #print("video_url : ", video_dict.get('video_url'))
            video_list.append(video_dict)

        return JsonResponse({'errno': 0, 'msg': "返回成功！", 'video': video_list}, safe=False)
    else:
        return JsonResponse({'errno': 0, 'msg': "请求方法错误！"})


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
        # print("数量 : ",)
        video_list = []
        for video in videos:
            video_dict = video.to_dict()
            #print("video_url: ", video_dict.get('video_url'))
            video_list.append(video_dict)

        return JsonResponse({'errno': 0, 'msg': "返回成功！", 'video': video_list}, safe=False)
    else:
        return JsonResponse({'errno': 0, 'msg': "请求方法错误！"})


def upload_video_method(video_file, video_id, ):
    client, bucket_name, bucket_region = get_cos_client()

    if video_id == '' or video_id == 0:
        video_id = str(uuid.uuid4())
    video_key = "video_file/{}".format(f'{video_id}.mp4')

    response_video = client.put_object(
        Bucket=bucket_name,
        Body=video_file,
        Key=video_key,
        StorageClass='STANDARD',
        ContentType="video/mp4"
    )
    video_url = ""
    if 'url' in response_video:
        video_url = response_video['url']
    else:
        video_url = f'https://{bucket_name}.cos.{bucket_region}.myqcloud.com/{video_key}'
    return video_url


def upload_photo_method(photo_file, photo_id):
    client, bucket_name, bucket_region = get_cos_client()

    if photo_id == '' or photo_id == 0:
        photo_id = str(uuid.uuid4())
    photo_key = "cover_file/{}".format(f'{photo_id}.png')
    response_photo = client.put_object(
        Bucket=bucket_name,
        Body=photo_file,
        Key=photo_key,
        StorageClass='STANDARD',
        ContentType="image/png"
    )
    photo_url = ""
    if 'url' in response_photo:
        photo_url = response_photo['url']
    else:
        photo_url = f'https://{bucket_name}.cos.{bucket_region}.myqcloud.com/{photo_key}'
    return photo_url

@csrf_exempt
def upload_video(request):
    if request.method == 'POST':
        # 获取上传的视频和封面文件
        user = request.user
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return JsonResponse({'errno':0, 'msg': "用户未登录！"})
        user_id =user.id
        label = request.POST.get('label')
        title = request.POST.get('title')
        description = request.POST.get('description')

        if len(title) == 0 or len(description) == 0:
            return JsonResponse({'errno':0, 'msg': "标题/描述不能为空！"})
        if label not in LABELS:
            return JsonResponse({'errno': 0, 'msg': "标签不合法！"})

        video_file = request.FILES.get('video_file')
        cover_file = request.FILES.get('cover_file')

        video = Video.objects.create(
            label=label,
            title=title,
            description=description,
            user_id=user_id,
            created_at=datetime.datetime.now(),
        )
        video_id = video.id
        video_url = upload_video_method(video_file, video_id)
        cover_url = upload_photo_method(cover_file, video_id)
        video.video_url = video_url
        video.cover_url = cover_url
        video.save()
        return JsonResponse({'errno': 0, 'msg': "上传成功"})
    else:
        return JsonResponse({'errno':0, 'msg': "请求方法错误！"})
def update_video(id,title,label,description,new_video,new_cover):
    try:
        video=Video.objects.get(id=id)
    except Video.DoesNotExist:
        return JsonResponse({'errno': 0, 'msg': '视频不存在'})
    if len(title)!=0:
        video.title=title
    if len(label)!=0 and label in LABELS:
        video.label=label
    if len(description) !=0:
        video.description=description
    if new_video:
        video_url = upload_video_method(new_video, video.id)
        video.video_url=video_url
    if new_cover:
        cover_url = upload_photo_method(new_video, video.id)
        video.cover_url=cover_url
    video.save()


def manage_video(request):
    if request.method == 'POST':
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
                return JsonResponse({'errno': 0, 'msg': '视频不存在'})
        elif op =='update':
            label = request.POST.get('label')
            title = request.POST.get('title')
            description = request.POST.get('description')
            new_video=request.POST.get('new_video')
            new_cover=request.POST.get('new_cover')
            update_video(video_id,title,label,description,new_video,new_cover)
        else:
            return JsonResponse({'errno': 0, 'msg': '操作不合法'})
    else:
        return JsonResponse({'errno': 0, 'msg': '请求方法不合法'})

def search_video(request):
    if request.method == 'GET':
        keyword = request.GET.get('keyword')
        if not keyword:
            return JsonResponse({'errno': 0, 'msg': '关键字不能为空'})
        # 使用 Q 对象进行模糊查询
        query = Q(title__icontains=keyword) | Q(description__icontains=keyword)
        videos = Video.objects.filter(query)
        video_list = []
        for video in videos:
            video_dict = video.to_dict()
            # print("video_url: ", video_dict.get('video_url'))
            video_list.append(video_dict)

        return JsonResponse({'errno': 0, 'msg': "返回成功！", 'video': video_list}, safe=False)
    else:
        return JsonResponse({'errno': 0, 'msg': "请求方法错误！"})


def view_video(request):
    if request.method == 'GET':
        # 这里可能需要把 不只是根据id获取视频，还有其他方式
        video_id = request.GET.get('video_id')
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return JsonResponse({'errno': 0, 'msg': '视频不存在'})
        # 将字典列表作为JSON响应返回
        video.view_amount+=1
        comments=Comment.objects.filter(video_id=video_id)
        comment_list=[]
        for c in comments:
            comment_list.append(c.to_dict())
        return JsonResponse({'errno': 0, 'msg': "返回成功！", 'video': video.to_dict(),'comment':comment_list}, safe=False)
    else:
        return JsonResponse({'errno': 0, 'msg': "请求方法错误！"})


@csrf_exempt
def comment_video(request):
    if request.method == 'POST':
        user_id = 1  # 测试用！！！
        video_id = request.POST.get('video_id')
        content = request.POST.get('content')
        created_at =  datetime.datetime.now()
        try:
            user = User.objects.get(id=user_id)
        
        except User.DoesNotExist:
            return JsonResponse({'errno': 0, 'msg': '用户不存在'})
        #print('video_id :',video_id)
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return JsonResponse({'errno': 0, 'msg': '视频不存在'})
        if len(content)==0:
            return JsonResponse({'errno': 0, 'msg': '评论不能为空'})
        comment = Comment.objects.create(
            user_id=user_id,
            content=content,
            video_id=video_id,
            created_at=created_at
        )
        comment.save()
        return JsonResponse({'errno': 0, 'msg': '评论成功'})
    else:
        return JsonResponse({'errno': 0, 'msg': "请求方法错误！"})


@csrf_exempt
def reply_comment(request):
    if request.method == 'POST':
        # 获取请求中传入的参数
        user_id=1
        comment_id = request.POST.get('comment_id')
        content = request.POST.get('content')
        try:
            comment=Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return JsonResponse({'errno': 0, 'msg': '评论不存在'})
        # 创建回复评论对象
        if len(content)==0:
            return JsonResponse({'errno': 0, 'msg': '回复不能为空'})
        reply = Reply(user_id=user_id, comment_id=comment_id, content=content)
        reply.save()
        # 构造返回给前端的数据
        return JsonResponse({'errno': 0, 'errmsg': 'success'})
    else:
        return JsonResponse({'errno': 0, 'msg': "请求方法错误！"})


@csrf_exempt
def like_video(request):
    if request.method == 'POST':
        # 获取请求中传入的参数
        user_id=1
        video_id = request.POST.get('video_id')
        try:
            video=Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return JsonResponse({'errno': 0, 'msg': "视频不存在！"})
        # 检查该用户是否已经点赞过该视频
        try:
            like = Like.objects.get(user_id=user_id, video_id=video_id)
            # 用户已经点赞过该视频，则取消点赞
            like.delete()
            video.like_amount-=1
            print('video.like_amount : ',video.like_amount)
            return JsonResponse({'errno': 0, 'msg': "点赞取消成功！"})
        except Like.DoesNotExist:
            # 用户没有点赞过该视频，则添加点赞记录
            like = Like(user_id=user_id, video_id=video_id)
            like.save()
            video.like_amount += 1
            print('video.like_amount : ',video.like_amount)
            return JsonResponse({'errno': 0, 'msg': "点赞成功！"})
    else:
        return JsonResponse({'errno': 0, 'msg': "请求方法错误！"})

def create_favorite(request):
    if request.method == 'POST':
        # 获取请求中传入的参数
        user_id = 1
        title = request.POST.get('title')
        description = request.POST.get('description')
        status =int(request.POST.get('status'))
        if len(description)==0 or not (status == 0 or status == 1):
            return JsonResponse({'errno': 0, 'msg': "参数不合法！"})
        try:
            favorite=Favorite.objects.get(user_id=user_id,title=title)
            return JsonResponse({'errno': 0, 'msg': "收藏夹已存在！"})
        except Favorite.DoesNotExist:
            if len(title)==0:
                favorite=Favorite(description=description,status=status,user_id=user_id,created_at=datetime.datetime.now())
            else:
                favorite=Favorite(title=title,description=description,status=status,user_id=user_id,created_at=datetime.datetime.now())
            favorite.save()
            return JsonResponse({'errno': 0, 'msg': "创建收藏夹成功！"})
    else:
        return JsonResponse({'errno': 0, 'msg': "请求方法错误！"})

def get_favorite(request):
    if request.method == 'GET':
        user_id=1
        try:
            favorite = Favorite.objects.filter(user_id=user_id)
            favorite_list=[]
            for f in favorite:
                favorite_list.append(f.to_dict())
            return JsonResponse({'errno': 0, 'favorite':favorite_list,'msg': "获取收藏夹成功！"})   
        except Favorite.DoesNotExist:
             return JsonResponse({'errno': 0, 'msg': "无收藏夹，请创建收藏夹！"})
    else:
         return JsonResponse({'errno': 0, 'msg': "请求方法错误！"})
    
def favorite_video(request):
    if request.method == 'POST':
        user_id = 1
        video_id=request.POST.get('video_id')
        favorite_id=request.POST.get('favorite_id')
        try:
            video=Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return JsonResponse({'errno': 0, 'msg': "视频不存在！"})
        try:
            favorite=Favorite.objects.get(id=favorite_id)
        except Favorite.DoesNotExist:
            return JsonResponse({'errno': 0, 'msg': "收藏夹不存在，请先创造收藏夹！"})
        try:
            fav_list=Favlist.objects.get(video_id=video_id,favorite_id=favorite_id)
            return JsonResponse({'errno': 0, 'msg': "已收藏！"})
        except Favlist.DoesNotExist:
            fav_list=Favlist(favorite_id=favorite_id,video_id=video_id,created_at=datetime.datetime.now())
            fav_list.save()
            video.fav_amount+=1
            return JsonResponse({'errno': 0, 'msg': "收藏成功！"})
    else:
        return JsonResponse({'errno': 0, 'msg': "请求方法错误！"})


