import time
from django.db import models
from qcloud_cos.cos_comm import CiDetectType
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import AnonymousUser
from decorator.decorator_permission import validate_login, validate_all
from django.http import JsonResponse
from django.core.mail import send_mail
from RookieVid_Backend import settings
from videos.cos_utils import Category, Label, SubLabel, get_cos_client
from videos.models import Video, Favorite, Favlist
from accounts.models import User, Follow, Vcode
from notifications.views import send_sys_notification
from notifications.models import Notification
import uuid
import smtplib
import os
import jwt
import re
import random
from django.utils import timezone
from datetime import datetime, timedelta


# Create your views here.

# 发送验证码
@csrf_exempt
def send_vcode(request):
    if request.method == 'POST':
        to_email = request.POST.get("email")
        print("to_email : ", to_email)
        if re.match('\w+@\w+.\w+', str(to_email)) is None:
            return JsonResponse({'errno': 1, 'msg': "邮箱格式错误"})
        # 通过邮箱判断用户是否已存在
        if User.objects.filter(email=to_email).exists():
            return JsonResponse({'errno': 1, 'msg': "邮箱已占用，请更换邮箱地址"})

        # 获取当前时间
        now_time = timezone.now()
        # 获取上次发送邮件的时间
        if Vcode.objects.filter(to_email=to_email).exists():
            codes = Vcode.objects.filter(to_email=to_email)
            for vcode in codes:
                if (now_time - vcode.send_at).seconds < 60:  # 1分钟内不能重复发送邮件
                    return JsonResponse({'errno': 1, 'msg': "操作过于频繁，请稍后再试"})
        # 随机生成一个新的验证码
        code = str(random.randint(10 ** 5, 10 ** 6 - 1))
        while Vcode.objects.filter(vcode=code).exists():
            code = str(random.randint(10 ** 5, 10 ** 6 - 1))
        EMAIL_FROM = "1151801165@qq.com"  # 邮箱来自
        email_title = '邮箱激活'
        email_body = "您的邮箱注册验证码为：{}, 该验证码有效时间为5分钟，请及时进行验证。".format(code)
        try:
            send_errno = send_mail(email_title, email_body, EMAIL_FROM, [to_email])
            if send_errno == 1:
                # 存储验证码
                new_vcode = Vcode(vcode=code, to_email=to_email)
                new_vcode.save()
                return JsonResponse({'errno': 0, 'msg': '验证码已发送，请查阅'})
            else:
                return JsonResponse(
                    {'errno': 1, 'msg': "验证码发送失败，请检查邮箱地址"})
        except smtplib.SMTPDataError:
            return JsonResponse(
                {'errno': 1, 'msg': "验证码发送失败，请检查邮箱地址"})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方式错误"})


# 先验证验证码是否正确，若正确检验用户名密码是否合法，完成注册
@csrf_exempt
def register(request):
    if request.method == 'POST':  # 判断请求方式是否为 POST（要求POST方式）
        # 获取输入的验证码和邮箱
        email = request.POST.get('email')
        vcode = request.POST.get('vcode')

        # 判断验证码是否失效
        now_time = timezone.now()
        # 获取发送验证码时间
        if Vcode.objects.filter(to_email=email).exists():
            if Vcode.objects.filter(vcode=vcode).exists():
                code = Vcode.objects.get(vcode=vcode)
                if (now_time - code.send_at).seconds <= 300:
                    code.delete()
                else:
                    # 该邮箱获取的验证码均已失效，删除
                    codes = Vcode.objects.filter(to_email=email)
                    for code in codes:
                        code.delete()
                    return JsonResponse({'errno': 1, 'msg': '验证码失效，请重新获取'})
            else:
                return JsonResponse({'errno': 1, 'msg': '验证码错误'})
        else:
            return JsonResponse({'errno': 1, 'msg': '该账户没有获取验证码'})

        # 验证码正确，进行注册
        username = request.POST.get('username')  # 获取请求数据
        password_1 = request.POST.get('password_1')
        password_2 = request.POST.get('password_2')

        # 用户名长度为1-20位
        if re.match('[\S]{1,20}', str(username)) is None:
            return JsonResponse({'errno': 1, 'msg': "用户名不合法"})
        # 密码长度为8-16位，且同时包含数字和字母
        if re.match('(?!^[0-9]+$)(?!^[a-zA-Z]+$)[0-9A-Za-z]{8,16}', str(password_1)) is None:
            return JsonResponse({'username': username, 'password': password_1, 'errno': 1, 'msg': "密码格式错误"})
        if password_1 != password_2:
            return JsonResponse({'errno': 1, 'msg': "两次输入的密码不同"})
        else:
            # 为用户分配不重复的uid
            uid = str(random.randint(10 ** 9, 10 ** 10 - 1))
            while User.objects.filter(uid=uid).exists():
                uid = str(random.randint(10 ** 9, 10 ** 10 - 1))
            # 数据库存取：新建 User 对象，赋值并保存
            new_user = User(uid=uid, username=username, password=password_1, email=email)
            new_user.save()  # 一定要save才能保存到数据库中
            content = '亲爱的' + new_user.username + "欢迎加入我们的大家庭！让我们一起开启一个精彩的旅程吧！"
            send_sys_notification(0, new_user.id, "RookieVid感谢您的加入", content, 0, 0)
            return JsonResponse({'uid': uid, 'errno': 0, 'msg': "注册成功"})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方式错误"})


@csrf_exempt
def login(request):
    if request.method == 'POST':
        uid = request.POST.get('uid')  # 获取请求数据
        password = request.POST.get('password')
        if User.objects.filter(uid=uid).exists():
            user = User.objects.get(uid=uid)
        elif User.objects.filter(email=uid).exists():
            user = User.objects.get(email=uid)
        else:
            return JsonResponse({'errno': 1, 'msg': "请先注册"})
        if user.password == password:  # 判断请求的密码是否与数据库存储的密码相同
            # request.session['id'] = user.uid
            payload = {'exp': datetime.utcnow()+timedelta(days=5), 'id': user.id}
            encode = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            # token = str(encode, encoding='utf-8')
            token = str(encode)
            print(encode)
            return JsonResponse({'token': token, 'user_id': user.id, 'status': user.status, 'errno': 0, 'msg': "登录成功"})
        else:
            return JsonResponse({'errno': 1, 'msg': "密码错误"})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方式错误"})


@csrf_exempt
def logout(request):
    request.session.flush()
    return JsonResponse({'errno': 0, 'msg': "注销成功"})


@csrf_exempt
@validate_login
def unsubscribe(request):
    if request.method == 'GET':
        user = request.user
        if Favorite.objects.filter(user_id=user.id).exists():
            favorites = Favorite.objects.filter(user_id=user.id)
            for favorite in favorites:
                favorite.delete()
        if Favlist.objects.filter(user_id=user.id).exists():
            favlists = Favlist.objects.filter(user_id=user.id)
            for favlist in favlists:
                favlist.delete()
        if Notification.objects.filter(send_to=user.id).exists():
            notifications = Notification.objects.filter(send_to=user.id)
            for notification in notifications:
                notification.delete()
        print(user.id)
        user.username = '用户已注销'
        user.email = ''
        user.password = ''
        user.avatar_url = 'https://aamofe-1315620690.cos.ap-beijing.myqcloud.com/avatar_file/default.png'
        user.signature = '删号跑路，江湖再见！'
        user.save()
        
        return JsonResponse({'errno': 0, 'msg': "用户注销成功", 'data': user.to_dict()})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方式错误"})
    

@csrf_exempt
@validate_login
def display_myprofile(request):
    # 看自己的个人中心
    if request.method == 'GET':
        user = request.user
        context = user.to_dict()
        following = Follow.objects.filter(follower_id=user.id).count()
        follower = Follow.objects.filter(following_id=user.id).count()
        return JsonResponse({'context': context, 'following': following, 'follower': follower, 'status': 0, 'errno': 0,
                             'msg': '查询用户信息成功'})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方式错误"})


@csrf_exempt
@validate_all
def display_profile(request):
    # 如果用户已登录，展示用户信息
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        user = request.user
        myid = -1
        print(type(user_id))
        if isinstance(user, AnonymousUser):
            is_login = 0
        else:
            is_login = 1
            myid = user.id

        if myid != -1 and int(user_id) == myid:  # 看自己的主页status是0，看别人的是1
            context = User.to_dict(user)
            following = Follow.objects.filter(follower_id=myid).count()
            follower = Follow.objects.filter(following_id=myid).count()
            return JsonResponse({'context': context, 'following': following, 'follower': follower, 'status': 0,
                                 'errno': 0, 'msg': '查询用户信息成功'})
        else:
            try:
                user = User.objects.get(id=user_id)
                context = User.to_dict(user)
                following = Follow.objects.filter(follower_id=user.id).count()
                follower = Follow.objects.filter(following_id=user.id).count()
                is_followed = 0
                if Follow.objects.filter(follower_id=request.user.id, following_id=user.id).exists():
                    is_followed = 1
                print(type(is_followed))
                return JsonResponse({'context': context, 'following': following, 'follower': follower, 'status': 1,
                                     'is_followed': is_followed, 'is_login': is_login, 'errno': 0, 'msg': '查询用户信息成功'})
            except User.DoesNotExist:
                return JsonResponse({'errno': 1, 'msg': '用户不存在'})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方式错误"})


@csrf_exempt
@validate_login
def edit_profile(request):
    if request.method == 'POST':
        print(request)
        username = request.POST.get('username')
        signature = request.POST.get('signature')
        # 能不能有自动填入之类的（？
        print(username)
        print(signature)
        if re.match('[\S]{1,20}', str(username)) is None:
            return JsonResponse({'errno': 1, 'msg': "用户名不合法"})
        if re.match('.{0,100}', str(signature)) is None:
            return JsonResponse({'errno': 2, 'msg': "个性签名太长啦"})
        user = request.user
        user.username = username
        user.signature = signature
        # 上传头像单独写
        user.save()
        return JsonResponse({'errno': 0, 'msg': "用户资料修改成功"})
    else:
        return JsonResponse({'error': 1, 'msg': "请求方式错误"})


def upload_avatar_method(avatar_file, avatar_id, url):
    client, bucket_name, bucket_region = get_cos_client()
    if avatar_id == '' or avatar_id == 0:
        avatar_id = str(uuid.uuid4())
    file_name = avatar_file.name
    file_extension = file_name.split('.')[-1]  # 获取文件后缀
    if file_extension == 'jpg':
        ContentType = "image/jpg"
    elif file_extension == 'jpeg':
        ContentType = "image/jpeg"
    elif file_extension == 'png':
        ContentType = "image/png"
    else:
        return -2, None, None
    avatar_key = f"{url}/{avatar_id}.{file_extension}"
    response_avatar = client.put_object(
        Bucket=bucket_name,
        Body=avatar_file,
        Key=avatar_key,
        StorageClass='STANDARD',
        ContentType=ContentType
    )
    if 'url' in response_avatar:
        avatar_url = response_avatar['url']
    else:
        avatar_url = f'https://{bucket_name}.cos.{bucket_region}.myqcloud.com/{avatar_key}'
    response_submit = client.get_object_sensitive_content_recognition(
        Bucket=bucket_name,
        BizType='f90478ee0773ac0ab139c875ae167353',
        Key=avatar_key,
        # DetectType=(CiDetectType.PORN | CiDetectType.ADS)
    )
    res = int(response_submit['Result'])
    Score=int(response_submit['Score'])
    if res == 1 or res==2 or Score>=60:
        category=response_submit['Category']
        label=response_submit['Label']
        subLabel=response_submit['SubLabel']
        if label=='Politics':
            #pprint.pprint(response_submit)

            content = "您的头像图片被判定为违规！" + \
                      "标签是" + Label[label] +  "，具体内容是：" + response_submit['PoliticsInfo']['Label'] + \
                      "。判定比例高达 " + str(Score) + "%。请修改"
        else:
            content = "您的头像图片被判定为违规！" +\
                  "标签是："+Label[label]+"，分类为："+Category[category]+"，具体内容是"+SubLabel[subLabel]+\
                  "。判定比例高达" + str(Score) + "%。请修改！"
        delete_avatar_method(url, avatar_id, file_extension)
        return 1,None,content
    # if res == 1:
    #    delete_avatar_method(avatar_id, file_extension)
    #    return res, avatar_url, response_submit['Label']
    return res, avatar_url, None


def delete_avatar_method(url,avatar_id,file_extension):
    client, bucket_name, bucket_region = get_cos_client()
    avatar_key = f"{url}/{avatar_id}.{file_extension}"
    response = client.delete_object(
                Bucket=bucket_name,
                Key=avatar_key
            )


@csrf_exempt
@validate_login
def edit_avatar(request):
    if request.method == 'POST':
        user = request.user
        avatar_file = request.FILES.get('avatar_file')
        print(request)
        print(avatar_file)
        if not avatar_file:
            return JsonResponse({'errno': 1, 'msg': "头像文件未上传"})
        # avatar_url = upload_photo_method(avatar_file, user.id)  # 头像的命名改成id

        avatar_id = user.id
        res, avatar_url, label = upload_avatar_method(avatar_file, avatar_id, "avatar_file")
        if res == -2:
            return JsonResponse({'errno': 1, 'msg': "图片格式不合法"})
        if res == 1:
            return JsonResponse({'errno': 1, 'msg': "上传失败！图片含有违规内容 ：" + label})

        client, bucket_name, bucket_region = get_cos_client()
        client.delete_object(
            Bucket=bucket_name,
            Key=user.avatar_url
        )
        user.avatar_url = avatar_url
        user.save()
        return JsonResponse({'errno': 0, 'msg': "头像上传成功"})

    else:
        return JsonResponse({'errno': 1, 'msg': "请求方式错误"})


@csrf_exempt
@validate_login
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        password_1 = request.POST.get('password_1')
        password_2 = request.POST.get('password_2')
        user = request.user
        if old_password != user.password:
            return JsonResponse({'errno': 1, 'msg': "密码错误，请重新输入"})
        if re.match('(?!^[0-9]+$)(?!^[a-zA-Z]+$)[0-9A-Za-z]{8,16}', str(password_1)) is None:
            return JsonResponse({'password': password_1, 'errno': 1, 'msg': "密码格式错误"})
        if password_1 != password_2:
            return JsonResponse({'errno': 1, 'msg': "两次输入的密码不同"})
        user.password = password_1
        user.save()
        return JsonResponse({'errno': 0, 'msg': "密码修改成功"})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方式错误"})


@csrf_exempt
@validate_login
def change_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        vcode = request.POST.get('vcode')
        # 判断验证码
        now_time = timezone.now()
        if Vcode.objects.filter(to_email=email).exists():
            if Vcode.objects.filter(vcode=vcode).exists():
                code = Vcode.objects.get(vcode=vcode)
                if (now_time - code.send_at).seconds <= 300:
                    code.delete()
                else:
                    # 该邮箱获取的验证码均已失效，删除
                    codes = Vcode.objects.filter(to_email=email)
                    for code in codes:
                        code.delete()
                    return JsonResponse({'errno': 1, 'msg': '验证码失效，请重新获取'})
            else:
                return JsonResponse({'errno': 1, 'msg': '验证码错误'})
        else:
            return JsonResponse({'errno': 1, 'msg': '该账户没有获取验证码'})

        user = request.user
        user.email = email
        user.save()
        return JsonResponse({'errno': 0, 'msg': '绑定邮箱修改成功'})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方式错误"})


@csrf_exempt
@validate_login
def create_follow(request):
    if request.method == 'POST':
        following_id = request.POST.get('following_id')  # 这里传入参数改成user.id
        print(request)
        print(following_id)
        try:
            User.objects.get(id=following_id)
        except User.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': "用户不存在"})
        follower_id = request.user.id
        follower_user = request.user.username
        if int(following_id) == follower_id:
            return JsonResponse({'errno': 1, 'msg': "无法关注自己的账号"})
        if Follow.objects.filter(follower_id=follower_id, following_id=following_id).exists():
            return JsonResponse({'errno': 1, 'msg': "已关注用户"})
        follow = Follow(follower_id=follower_id, following_id=following_id)
        follow.save()
        send_sys_notification(follower_id, following_id, '新增关注', f'{follower_user}开始关注你啦', 0, 0)
        follower_num = Follow.objects.filter(following_id=following_id).count()
        resp = {'follower': follower_id, 'following': int(following_id), 'follower_num': follower_num, 'errno': 0, 'msg': '关注成功'}
        return JsonResponse(resp)
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方式错误"})


@csrf_exempt
@validate_login
def remove_follow(request):
    if request.method == 'POST':
        following_id = request.POST.get('following_id')  # 传入参数改成user.id
        follower_id = request.user.id
        try:
            follow = Follow.objects.get(follower_id=follower_id, following_id=following_id)
            follow.delete()
            follower_num = Follow.objects.filter(following_id=following_id).count()
            resp = {'follower': follower_id, 'following': int(following_id), 'follower_num': follower_num, 'errno': 0, 'msg': '取关成功'}
            return JsonResponse(resp)
        except Follow.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': "未关注用户"})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方式错误"})


@csrf_exempt
@validate_login
def get_followings(request):
    if request.method == 'GET':
        following_list = []
        user_id = request.user.id
        if Follow.objects.filter(follower_id=user_id).exists():
            followings = Follow.objects.filter(follower_id=user_id)
            for following in followings:
                following_user = User.objects.get(id=following.following_id)
                following_data = User.to_simple_dict(following_user)
                following_list.append(following_data)
            return JsonResponse({'errno': 0, 'msg': "关注列表查询成功", 'data': following_list})
        else:
            return JsonResponse({'errno': 0, 'msg': "关注列表为空", 'data': following_list})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})


@csrf_exempt
@validate_login
def get_followers(request):
    if request.method == 'GET':
        follower_list = []
        user_id = request.user.id
        if Follow.objects.filter(following_id=user_id).exists():
            followers = Follow.objects.filter(following_id=user_id)
            for follower in followers:
                follower_user = User.objects.get(id=follower.follower_id)
                follower_data = User.to_simple_dict(follower_user)
                follower_data['is_refollowed'] = 0
                if Follow.objects.filter(following_id=follower_user.id, follower_id=user_id).exists():
                    follower_data['is_refollowed'] = 1
                follower_list.append(follower_data)
            return JsonResponse({'errno': 0, 'msg': "粉丝列表查询成功", 'data': follower_list})
        else:
            return JsonResponse({'errno': 0, 'msg': "粉丝列表为空", 'data': follower_list})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})


@csrf_exempt
@validate_all
def get_videos(request):
    if request.method == 'GET':
        video_list = []
        user_id = request.GET.get('user_id')
        print(request)
        # print('user_id='+user_id)
        if Video.objects.filter(user_id=user_id).exists():
            videos = Video.objects.filter(user_id=user_id)
            for video in videos:
                video_data = Video.to_simple_dict(video)
                video_list.append(video_data)
            return JsonResponse({'errno': 0, 'msg': "投稿列表查询成功", 'data': video_list})
        else:
            return JsonResponse({'errno': 0, 'msg': "投稿列表为空", 'data': video_list})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})


@csrf_exempt
@validate_all
def get_favorite(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        user = request.user
        print(int(user_id) == user.id)

        try:
            if int(user_id) == user.id:  # 看自己的收藏夹
                favorites = Favorite.objects.filter(user_id=user_id)
            else:
                favorites = Favorite.objects.filter(user_id=user_id, is_private=0)
            favorite_list = []
            for favorite in favorites:
                favorite_list.append(Favorite.to_dict(favorite))
            return JsonResponse({'errno': 0, 'favorite': favorite_list, 'msg': "获取收藏夹成功"})
        except Favorite.DoesNotExist:
            return JsonResponse({'errno': 0, 'msg': "用户未创建收藏夹"})

    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})


@csrf_exempt
@validate_all
def get_favlist(request):
    if request.method == 'GET':
        favorite_id = request.GET.get('favorite_id')
        print(request)
        print(favorite_id)
        video_list = []
        try:
            favorite = Favorite.objects.get(id=favorite_id)
        except Favorite.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': "收藏夹不存在", 'data': video_list})

        if Favlist.objects.filter(favorite_id=favorite_id).exists():
            favlists = Favlist.objects.filter(favorite_id=favorite_id)
            for favlist in favlists:
                if Video.objects.filter(id=favlist.video_id).exists():
                    video = Video.objects.get(id=favlist.video_id)
                    video_data = Video.to_simple_dict(video)
                    video_list.append(video_data)
            return JsonResponse({'errno': 0, 'msg': "收藏列表查询成功", 'data': video_list, 'cover_url': favorite.cover_url})
        else:
            return JsonResponse({'errno': 0, 'msg': "收藏夹为空", 'data': video_list, 'cover_url': favorite.cover_url})

    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})


@csrf_exempt
@validate_login
def delete_favorite(request):
    if request.method == 'POST':
        favorite_id = request.POST.get('favorite_id')
        print(favorite_id)
        try:
            favorite = Favorite.objects.get(id=favorite_id)
        except Favorite.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': "收藏夹不存在"})
        user_id = favorite.user_id
        if user_id != request.user.id:   # 最好是进别人的主页不显示删除按钮
            return JsonResponse({'errno': 1, 'msg': "没有操作权限"})

        if Favlist.objects.filter(favorite_id=favorite_id).exists():
            favlists = Favlist.objects.filter(favorite_id=favorite_id)
            for favlist in favlists:
                favlist.delete()
        favorite = Favorite.objects.get(id=favorite_id)
        favorite.delete()
        return JsonResponse({'errno': 0, 'msg': "收藏夹删除成功"})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方法错误"})


@csrf_exempt
@validate_login
def delete_favorite_video(request):
    if request.method == 'POST':
        favorite_id = request.POST.get('favorite_id')
        delete = request.POST.getlist('delete_id')
        user = request.user
        try:
            for video_id in delete:
                favorite_video = Favlist.objects.get(favorite_id=favorite_id, video_id=video_id)
                if favorite_video.user_id != user.id:
                    return JsonResponse({'errno': 1, 'msg': "没有操作权限"})
                if not Video.objects.filter(id=video_id).exists():
                    favorite_video.delete()
                    return JsonResponse({'errno': 0, 'msg': "视频失效，已移除收藏"})
                favorite_video.delete()
            return JsonResponse({'errno': 0, 'msg': "取消收藏成功"})
        except Favlist.DoesNotExist:
            return JsonResponse({'errno': 1, 'msg': "视频已删除或不存在"})
    else:
        return JsonResponse({'error': 1, 'msg': "请求方式错误"})
