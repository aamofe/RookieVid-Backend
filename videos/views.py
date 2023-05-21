import datetime
import json
import pprint
import uuid

from qcloud_cos.cos_comm import CiDetectType
from qcloud_cos import CosServiceError
from decorator.decorator_permission import validate_login, validate_all
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q, Count, F, ExpressionWrapper
from django.db import models
from django.core import serializers
import datetime
from accounts.models import User, Follow
from super_admin.models import Complain
from videos.cos_utils import get_cos_client
from videos.models import Video, Like, Comment, Reply, Favorite, Favlist
from random import sample
from django.contrib.auth.models import AnonymousUser
# 视频分类标签
LABELS = ['娱乐', '军事', '生活', '音乐', '学习', '科技', '运动', '游戏', '影视', '美食']
@validate_all
def get_video_by_label(request):
    if request.method == 'GET':
        label = request.GET.get('label')
        num=request.GET.get('num')
        if label not in LABELS:
            return JsonResponse({'errno': 1, 'msg': "标签错误！"})
        if len(num)==0 or not num.isdigit():
            return JsonResponse({'errno': 1, 'msg': "视频数量错误！"})
        else:
            num=int(num)
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
        return JsonResponse({'errno': 1, 'msg': "请求方法错误！"})

@validate_all
def get_video_by_hotness(request):
    if request.method == 'GET':
        # 构建热度计算表达式
        num=request.GET.get('num')
        if len(num)==0 or not num.isdigit():
            return JsonResponse({'errno': 1, 'msg': "视频数量错误！"})
        else:
            num=int(num)
        hotness_expression = ExpressionWrapper(
            Count('like_amount') + F('view_amount') * 0.5,
            output_field=models.FloatField()
        )
        # 获取符合条件的视频，并按热度计算排序
        videos = Video.objects.filter(reviewed_status=1).annotate(
            hotness_score=hotness_expression
        ).order_by('-hotness_score', '-like_amount', '-view_amount', 'id')
        # 获取前6个视频
        videos = videos[:(2*num)]
        videos = sample(list(videos),num)
        # print("数量 : ",)
        video_list = []
        for video in videos:
            video_dict = video.to_dict()
            #print("video_url: ", video_dict.get('video_url'))
            video_list.append(video_dict)

        return JsonResponse({'errno': 0, 'msg': "返回成功！", 'video': video_list}, safe=False)
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误！"})
@validate_all
def get_related_video(request):
    if request.method == 'GET':
        video_id=request.GET.get('video_id')
        num=request.GET.get('num')
        if not video_id.isdigit():
            return JsonResponse({'errno': 1, 'msg': "视频ID错误！"})
        if len(num)==0 or not num.isdigit():
            return JsonResponse({'errno': 1, 'msg': "视频数量错误！"})
        else:
            num=int(num)
        try:
            video=Video.objects.get(id=video_id)
            
            videos=Video.objects.filter(Q(user_id=video.user_id)|Q (label=video.label),reviewed_status=1)
            if num==0:
                return JsonResponse({'errno': 1, 'msg': "参数不合法！"})
            video_list=[]
            random_videos = sample(list(videos), num)
            for video in random_videos:
                video_dict = video.to_simple_dict()
                video_list.append(video_dict)
            return JsonResponse({'errno': 0, 'msg': "返回成功！", 'video': video_list}, safe=False)
        except Video.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': "视频不存在！"})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误！"})

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
@validate_login
def upload_video(request):
    if request.method == 'POST':
        # 获取上传的视频和封面文件
        user = request.user
        user_id =user.id
        label = request.POST.get('label')
        title = request.POST.get('title')
        description = request.POST.get('description')
        if len(label)==0:
            return JsonResponse({'errno': 1, 'msg': "标签不能为空！"})
        if len(title) == 0 :
            return JsonResponse({'errno':1, 'msg': "标题不能为空！"})
        if len(description) == 0:
            return JsonResponse({'errno': 1, 'msg': "描述不能为空！"})
        if label not in LABELS:
            return JsonResponse({'errno': 1, 'msg': "标签不合法！"})

        video_file = request.FILES.get('video_file')
        cover_file = request.FILES.get('cover_file')
        #添加对video_file的审核，只能为.mp4格式 并且是可以打开的视频文件

        video = Video.objects.create(
            label=label,
            title=title,
            description=description,
            user_id=user_id,
            created_at=datetime.datetime.now(),
        )
        video_id = video.id
        cover_id=video_id
        client, bucket_name, bucket_region = get_cos_client()

        if cover_id == '' or cover_id == 0:
            cover_id = str(uuid.uuid4())
        #上传图片
        file_name = cover_file.name
        file_extension = file_name.split('.')[-1]  # 获取文件后缀
        if file_extension =='jpg':
            ContentType = "image/jpg"
        elif file_extension =='jpeg':
            ContentType = "image/jpeg"
        elif file_extension =='png':
            ContentType = "image/png"
        else :
            return JsonResponse({'errno': 1, 'msg': "图片格式不合法"})
        cover_key = f"cover_file/{cover_id}.{file_extension}"
        response_photo = client.put_object(
            Bucket=bucket_name,
            Body=cover_file,
            Key=cover_key,
            StorageClass='STANDARD',
            ContentType=ContentType
        )
        if 'url' in response_photo:
            cover_url = response_photo['url']
        else:
            cover_url = f'https://{bucket_name}.cos.{bucket_region}.myqcloud.com/{cover_key}'
        #图片自动审核
        response_submit = client.get_object_sensitive_content_recognition(
            Bucket=bucket_name,
            BizType='f90478ee0773ac0ab139c875ae167353',
            Key=cover_key,
            DetectType=(CiDetectType.PORN | CiDetectType.ADS)
        )
        res = int(response_submit['Result'])
        if res == 1:
            video.delete()
            response = client.delete_object(
                Bucket=bucket_name,
                Key=cover_key
            )
            return JsonResponse({'errno': 1, 'msg': "上传失败！图片含有违规内容 ：" + response_submit['Label']})


        #上传视频
        if video_id == '' or video_id == 0:
            video_id = str(uuid.uuid4())
        file_name = cover_file.name
        file_extension = file_name.split('.')[-1]  # 获取文件后缀
        if not file_extension =='mp4':
            return JsonResponse({'errno': 1, 'msg': "视频格式不合法"})
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
        #视频自动审核
        if video_id == '' or video_id == 0:
            video_id = str(uuid.uuid4())
        video_key = "video_file/{}".format(f'{video_id}.mp4')
        response_submit = client.ci_auditing_video_submit(
            Bucket=bucket_name,
            BizType='8f7d7f7e0393f74ee5de3394bc7bfeb1',
            Key=video_key,
        )
        video.video_url = video_url
        video.cover_url = cover_url
        video.save()
        return JsonResponse({'errno': 0, 'msg': "上传成功,待审核"})
    else:
        return JsonResponse({'errno':1, 'msg': "请求方法错误！"})

def call_back(request):
    client, bucket_name, bucket_region = get_cos_client()
    if request.method=='POST':
        body = json.loads(request.body)
        code = body.get("code")#错误码，值为0时表示审核成功，非0表示审核失败
        data = body.get("data")#视频审核结果的详细信息。
        JobId = data.get("JobId")
        url = data.get("url")
        result = int(data.get("result"))
        porn_info = data.get("porn_info")#审核场景为涉黄的审核结果信息。
        # "hit_flag": 0 ,"label": "","count": 0
        ads_info=data.get("ads_info")
        label=''
        if len(porn_info['label'])!=0:
            label+=porn_info['label']
        if len(ads_info['label'])!=0:
            label+=porn_info['label']
        video=Video.objects.get(JobId=JobId)
        user_id = video.user_id
        # 删除审核记录
        video.JobId=None
        video.save()
        user=User.objects.get(id=video.user_id)
        file_extension = video.cover_url.split('.')[-1]  # 获取文件后缀
        cover_key = f"cover_file/{video.id}.{file_extension}"
        video_key = "video_file/{}".format(f'{video.id}.mp4')
        if result==0:#审核正常
            video.reviewed_status=1#审核通过
            #给up主发信息
            title = "视频发布成功！"
            content = "亲爱的" + user.username + '你好呀!\n' '视频审核通过啦，快和小伙伴分享分享你的视频叭~'
            #create_message(user_id, title, content)
            #给所有粉丝发信息
            fan_list=Follow.objects.filter(following_id=user.id)
            for fan in fan_list:
                fan_id=fan.follower_id
                title = "你关注的博主发布新视频啦！"
                content = "亲爱的" + User.objects.get(id=fan_id).username + '你好呀!\n''你关注的博主发布新视频啦！快去看看，然后在评论区留下自己的感受叭~'
                #create_message(fan_id, title, content)
        elif result==1:
            video.delete()
            response = client.delete_object(
                Bucket=bucket_name,
                Key=cover_key
            )
            response = client.delete_object(
                Bucket=bucket_name,
                Key=video_key
            )
            title = "视频审核失败！"
            content = "亲爱的" + user.username + ' 你好呀!\n视频内容好像带有一点' + label + '呢！\n下次不要再上传这类的视频了哟，这次就算了嘿嘿~'
            # (user_id, title, content)
            #给up主发信息
        elif result==2:
            #给up主发信息
            title = "视频需要人工审核！"
            content = "亲爱的" + user.username + ' 你好呀!\n视频内容好像带有一点' + label + '呢！\n我们需要人工再进行审核，不要着急哦~'
            #发信息(user_id, title, content)

@validate_login
def delete_video(request):
    if request.method == 'POST':
        # 获取操作类型和视频ID
        user=request.user
        video_id = request.GET.get('video_id')
        try:
            # 根据视频ID从数据库中删除该视频记录
            video = Video.objects.get(id=video_id)
            if user.id!=video.user_id:
                return JsonResponse({'errno': 1, 'msg': '没有权限删除'})
            video.delete()
            return JsonResponse({'errno': 0, 'msg': '删除成功'})
        except Video.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': '视频不存在'})
    else:
        return JsonResponse({'errno': 1, 'msg': '请求方法不合法'})

@validate_login   
def update_video(request):
    if request.method == 'POST':
        user=request.user
        video_id = request.GET.get('video_id')
        label = request.POST.get('label')
        title = request.POST.get('title')
        description = request.POST.get('description')
        video_file=request.FILES.get('video_file')
        cover_file=request.FILES.get('cover_file')

        try:
            video = Video.objects.get(id=video_id)
            if user.id !=video.user_id:
                return JsonResponse({'errno':1, 'msg': '没有权限更新'})
            res=0
            if title:
                video.title = title
                res+=1
            if label and label!=video.label:
                if label in LABELS :
                    video.label = label
                    res+=1
                else:
                    return JsonResponse({'errno': 1, 'msg': '标签不合法'})
            if  description and description!=video.description:
                video.description = description
                res+=1
            if video_file:
                video_url = upload_video_method(video_file, video.id)
                video.video_url = video_url
                res+=1
            if cover_file:
                cover_url = upload_photo_method(cover_file, video.id)
                video.cover_url = cover_url
                res+=1
            if res==0:
                return JsonResponse({'errno': 1, 'msg': '没有更新'})
            video.save()
            return JsonResponse({'errno': 0, 'msg': '更新成功'})
        except Video.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': '视频不存在'})
    else:
        return JsonResponse({'errno': 1, 'msg': '请求方法不合法'})
    
@validate_login
def get_video(request):
    if request.method == 'GET':
        user=request.user
        print('hhhh ',user.id)
        try:
            videos=Video.objects.filter(user_id=user.id)
            video_list=[]
            for v in videos:
                video_list.append(v.to_simple_dict())
            return JsonResponse({'errno': 0, 'video':video_list,'msg': '获取稿件成功'})
        except Video.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': '没有上传稿件'})
    else:
        return JsonResponse({'errno': 1, 'msg': '请求方法不合法'})
@validate_all
def search(request):
    if request.method == 'GET':
        keyword = request.GET.get('keyword')
        if not keyword:
            return JsonResponse({'errno': 1, 'msg': '关键字不能为空'})
        # 使用 Q 对象进行模糊查询
        query_video = Q(title__icontains=keyword) | Q(description__icontains=keyword)
        videos = Video.objects.filter(query_video)
        query_user = Q(username__icontains=keyword) | Q(signature__icontains=keyword)
        users=User.objects.filter(query_user)
        video_list = []
        user_list=[]
        for v in videos:
            video_dict = v.to_dict()
            # print("video_url: ", video_dict.get('video_url'))
            video_list.append(video_dict)
        for u in users:
            user_list.append(u.to_dict())
        return JsonResponse({'errno': 0, 'msg': "返回成功！", 'video': video_list,'user':user_list}, safe=False)
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误！"})



@validate_all
def view_video(request):
    if request.method == 'GET':
        video_id = request.GET.get('video_id')
        if not video_id.isdigit():
            return JsonResponse({'errno': 1, 'msg': '视频id不合法！'})
        try:
            video = Video.objects.get(id=video_id)
            # 将字典列表作为JSON响应返回
            video.view_amount += 1
            v=video.to_dict()
            user = request.user
            user_id=user.id
            if isinstance(user, AnonymousUser):
                liked=0
                favorited = 0
            else:
                try :
                    like=Like.objects.get(video_id=video_id,user_id=user_id)
                    liked=1
                except Like.DoesNotExist:
                    liked=0
                try:
                    favorite=Favlist.objects.get(video_id=video_id,user_id=user_id)
                    favorited=1
                except:
                    favorited=0
            v['liked']=liked
            v['favorited']=favorited
            total_comment_amount=0
            comment_amount=0
            comments = Comment.objects.filter(video_id=video_id)
            comment_list = []
            for c in comments:
                cc=c.to_dict()
                comment_list.append(cc)
                total_comment_amount+=cc['reply_amount']+1
                comment_amount+=1
            v['total_comment_amount'] =total_comment_amount
            v['comment_amount'] =comment_amount
            return JsonResponse({'errno': 0, 'msg': "返回成功！", 'video': v, 'comment': comment_list},safe=False)
        except Video.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': '视频不存在'})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误！"})

def get_comment(request):
    if request.method == 'GET':
        video_id=request.GET.get('video_id')
        try:
            video=Video.objects.get(id=video_id)
            comments = Comment.objects.filter(video_id=video_id)
            comment_list = []
            for c in comments:
                cc = c.to_dict()
                comment_list.append(cc)
            return JsonResponse({'errno': 0, 'msg': "返回成功！", 'comment': comment_list}, safe=False)
        except Video.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': '视频不存在'})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误！"})
@csrf_exempt
@validate_login
def comment_video(request):
    if request.method == 'POST':
        user = request.user
        user_id=user.id
        video_id = request.POST.get('video_id')
        content = request.POST.get('content')
        created_at =  datetime.datetime.now()
        try:
            video = Video.objects.get(id=video_id)
            if len(content) == 0:
                return JsonResponse({'errno': 1, 'msg': '评论不能为空'})
            comment = Comment.objects.create(
                user_id=user_id,
                content=content,
                video_id=video_id,
                created_at=created_at
            )
            comment.save()
            return JsonResponse({'errno': 0, 'msg': '评论成功'})
        except Video.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': '视频不存在'})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误！"})
@validate_login
def delete_comment(request):
    if request.method=='POST':
        user=request.user
        comment_id=request.POST.get('comment_id')
        try:
            comment=Comment.objects.get(id=comment_id)
            try:
                #video=Video.objects.get(id=comment.video_id)
                video = Video.objects.get(id=comment.video_id)
                if not (user.id == comment.user_id or user.id == video.user_id or user.status == 1):
                    return JsonResponse({'errno': 1, 'msg': "没有权限删除评论！"})
                reply = Reply.objects.filter(comment_id=comment_id)
                for r in reply:
                    r.delete()
                comment.delete()
                return JsonResponse({'errno': 0, 'msg': "删除评论成功！"})
            except:
                return JsonResponse({'errno': 1, 'msg': "视频不存在！"})
        except Comment.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': "评论不存在！"})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误！"})
@csrf_exempt
@validate_login
def reply_comment(request):
    if request.method == 'POST':
        # 获取请求中传入的参数
        user = request.user
        user_id = user.id
        comment_id = request.POST.get('comment_id')
        content = request.POST.get('content')
        video_id=request.POST.get('video_id')
        try:
            comment=Comment.objects.get(id=comment_id)
            try:
                video = Video.objects.get(id=video_id)
                if len(content) == 0:
                    return JsonResponse({'errno': 1, 'msg': '回复不能为空'})
                reply = Reply(user_id=user_id, comment_id=comment_id, content=content, video_id=video_id)
                reply.save()
                return JsonResponse({'errno': 0, 'errmsg': '回复成功'})
            except Video.DoesNotExist:
                return JsonResponse({'errno': 1, 'msg': '视频不存在'})
        except Comment.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': '评论不存在'})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误！"})
@validate_login
def delete_reply(request):
    if request.method=='POST':
        user=request.user
        reply_id=request.POST.get('reply_id')
        try:
            reply=Reply.objects.get(id=reply_id)
            try:
                comment = Comment.objects.get(id=reply.comment_id)
                try:
                    video = Video.objects.get(id=reply.video_id)
                    if not (user.id == comment.user_id or user.id == reply.user_id or user.id == video.user_id or user.status == 1):
                        return JsonResponse({'errno': 1, 'msg': "没有权限删除回复！"})
                    reply.delete()
                    return JsonResponse({'errno': 0, 'msg': "删除回复成功！"})
                except:
                    return JsonResponse({'errno': 1, 'msg': "视频不存在！"})
            except:
                return JsonResponse({'errno': 1, 'msg': "评论不存在！"})
        except Comment.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': "回复不存在！"})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误！"})

@csrf_exempt
@validate_login
def like_video(request):
    if request.method == 'POST':
        # 获取请求中传入的参数
        user = request.user
        user_id = user.id
        video_id = request.POST.get('video_id')
        print('hahha',user.id)
        try:
            video=Video.objects.get(id=video_id)
            # 检查该用户是否已经点赞过该视频
            try:
                like = Like.objects.get(user_id=user_id, video_id=video_id)
                # 用户已经点赞过该视频，则取消点赞
                like.delete()
                video.like_amount -= 1
                if video.like_amount < 0:
                    video.like_amount = 0
                video.save()
                # print('video.like_amount : ',video.like_amount)
                return JsonResponse({'errno': 1, 'msg': "点赞取消成功！"})
            except Like.DoesNotExist:
                # 用户没有点赞过该视频，则添加点赞记录
                like = Like(user_id=user_id, video_id=video_id)
                like.save()
                video.like_amount += 1
                video.save()
                # ('video.like_amount : ',video.like_amount)
                return JsonResponse({'errno': 0, 'msg': "点赞成功！"})
        except Video.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': "视频不存在！"})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误！"})
@validate_login
def create_favorite(request):
    if request.method == 'POST':
        # 获取请求中传入的参数
        user = request.user
        user_id=user.id
        print('hah',user_id)
        title = request.POST.get('title')
        description = request.POST.get('description')
        status =int(request.POST.get('status'))
        if len(description)==0 or not (status == 0 or status == 1):
            return JsonResponse({'errno': 1, 'msg': "参数不合法！"})
        try:
            favorite=Favorite.objects.get(user_id=user_id,title=title)
            return JsonResponse({'errno': 1, 'msg': "收藏夹已存在！"})
        except Favorite.DoesNotExist:
            if len(title)==0:
                favorite=Favorite(description=description,status=status,user_id=user_id,created_at=datetime.datetime.now())
            else:
                favorite=Favorite(title=title,description=description,status=status,user_id=user_id,created_at=datetime.datetime.now())
            favorite.save()
            return JsonResponse({'errno': 0, 'msg': "创建收藏夹成功！"})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误！"})
@validate_login
def get_favorite(request):#判断是否已收藏
    if request.method == 'GET':
        user=request.user
        user_id=user.id
        video_id=request.GET.get('video_id')
        favorite_list = []
        try:
            favorite = Favorite.objects.filter(user_id=user_id)
            for f in favorite:
                ff = f.to_dict()
                try:
                    favlist = Favlist.objects.get(video_id=video_id, favorite_id=f.id)
                    ff['favorited'] = 1
                except Favlist.DoesNotExist:
                    ff['favorited'] = 0
                favorite_list.append(ff)
            return JsonResponse({'errno': 0, 'favorite':favorite_list,'msg': "获取收藏夹成功！"})
        except Favorite.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': "无收藏夹，请创建收藏夹！"})
    else:
         return JsonResponse({'errno': 1, 'msg': "请求方法错误！"})

@validate_login
def favorite_video(request):
    if request.method == 'POST':
        user = request.user
        user_id = user.id
        video_id=request.POST.get('video_id')
        favorite_list=request.POST.getlist('favorite_list',[])
        print(len(favorite_list))
        try:
            video=Video.objects.get(id=video_id)
            for f_id in favorite_list : #添加收藏
                try:
                    favorite=Favorite.objects.get(id=f_id,user_id=user_id)
                except:
                    return JsonResponse({'errno': 1, 'msg': "收藏夹不属于用户！"})
                try :
                    favlist=Favlist.objects.get(favorite_id=f_id,video_id=video_id)
                except Favlist.DoesNotExist:
                    favlist=Favlist(user_id=user_id,favorite_id=f_id,video_id=video_id,created_at=datetime.datetime.now())
                    favlist.save()
            favorites=Favorite.objects.filter(user_id=user_id)
            for f in favorites:#取消收藏
                #print("???",type(f.id),type(favorite_list[0]))
                if str(f.id) not in favorite_list :
                    try :
                        favorite=Favlist.objects.get(favorite_id=f.id,video_id=video_id)
                        favorite.delete()
                    except Favlist.DoesNotExist:
                        pass
            return JsonResponse({'errno': 0, 'msg': "收藏成功！"})
        except Video.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': "视频不存在！"})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误！"})


@validate_login
def is_complaint(request):
    if request.method=='GET':
        user=request.user
        video_id=request.POST.get('video_id')
        created_at=datetime.datetime.now()
        try:
            complain=Complain.objects.get(video_id=video_id,user_id=user.id)
            if (complain.created_at-created_at).seconds<3600:
                return JsonResponse({'errno': 0,'is_complaint':1, 'msg': "投诉间隔小于1小时！"})
            else:
                return JsonResponse({'errno': 0, 'is_complaint': 0, 'msg': "可以投诉！"})
        except Complain.DoesNotExist:
            return JsonResponse({'errno': 0,'is_complaint':0, 'msg': "可以投诉！"})
@validate_login
def complain_video(request):
    if request.method=='POST':
        user=request.user
        video_id=request.POST.get('video_id')
        content=request.POST.get('content')
        created_at=datetime.datetime.now()
        try :
            video=Video.objects.get(id=video_id)
            if len(content)==0:
                return JsonResponse({'errno': 1, 'msg': "投诉原因不能为空！"})
            complain = Complain(video_id=video_id, user_id=user.id, reason=content, created_at=created_at,status=0)
            complain.save()
            return JsonResponse({'errno': 0, 'msg': "投诉成功！"})
        except Video.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': "视频不存在！"})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误！"})




