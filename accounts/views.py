import time

from django.shortcuts import render
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail

from accounts.models import User, Follow, Vcode
import re
import random


# Create your views here.

# 发送验证码
@csrf_exempt
def send_mail_vcode(request):
    to_email = request.POST.get("email")
    print("to_email : ", to_email)
    if re.match('\w+@\w+.\w+', str(to_email)) is None:
        return JsonResponse({'errno': 1004, 'msg': "邮箱格式错误"})
    # 获取当前时间
    now_time = time.time()
    # 获取上次发送邮件的时间
    mail_code_time = request.session.get('mail_code_time')
    if mail_code_time and now_time < mail_code_time + 60:  # 1分钟内不能重复发送邮件
        return JsonResponse({'errno': 1005, 'msg': "操作过于频繁，请稍后再试"})
    else:
        # 随机生成一个新的验证码
        code = str(random.randint(10 ** 5, 10 ** 6 - 1))
        while Vcode.objects.filter(vcode=code).exists():
            code = str(random.randint(10 ** 5, 10 ** 6 - 1))
        EMAIL_FROM = "1151801165@qq.com"  # 邮箱来自
        email_title = '邮箱激活'
        email_body = "您的邮箱注册验证码为：{}, 该验证码有效时间为5分钟，请及时进行验证。".format(code)
        send_errno = send_mail(email_title, email_body, EMAIL_FROM, [to_email])
        if send_errno == 1:
            # 存储验证码
            new_vcode = Vcode(vcode=code, to_email=to_email)
            new_vcode.save()
            resp = {'errno': 1000, 'msg': '验证码已发送，请查阅'}

        else:
            return JsonResponse(
                {'from': EMAIL_FROM, 'to': to_email, 'errno': 1006, 'msg': "验证码发送失败，请检查邮箱地址"})

        # 存储发送邮件时间
        request.session['mail_code_time'] = time.time()
    return JsonResponse(resp)


# 先验证验证码是否正确，若正确检验用户名密码是否合法，完成注册
@csrf_exempt
def register(request):
    if request.method == 'POST':  # 判断请求方式是否为 POST（要求POST方式）
        # 获取输入的验证码和邮箱
        email = request.POST.get('email')
        vcode = request.POST.get('vcode')

        # 判断验证码是否失效
        now_time = time.time()
        # 获取发送验证码时间
        session_code_time = request.session.get('mail_code_time')
        if session_code_time and now_time <= session_code_time + 300:
            # 检测验证码是否存在于数据库中
            if Vcode.objects.filter(vcode=vcode).exists():
                code = Vcode.objects.get(vcode=vcode)
                if code.to_email != email:
                    return JsonResponse({'errno': 1009, 'msg': '该账户没有获取验证码'})
                else:
                    # 从数据库中删除该验证码
                    code.delete()
            else:
                return JsonResponse({'errno': 1007, 'msg': '验证码错误'})
        else:
            print("存储时间 ： ",session_code_time," 现在时间 : ",now_time)
            return JsonResponse({'errno': 1008, 'msg': '验证码失效，请重新获取'})

        # 验证码正确，进行注册
        username = request.POST.get('username')  # 获取请求数据
        password_1 = request.POST.get('password_1')
        password_2 = request.POST.get('password_2')
        # 通过邮箱判断用户是否已存在
        if User.objects.filter(email=email).exists():
            return JsonResponse({'errno': 1010, 'msg': "账号已存在，请勿重复注册"})
        # 用户名长度为1-20位
        if re.match('.{1,20}', str(username)) is None:
            return JsonResponse({'errno': 1001, 'msg': "用户名不合法"})
        # 密码长度为8-16位，且同时包含数字和字母
        if re.match('(?!^[0-9]+$)(?!^[a-zA-Z]+$)[0-9A-Za-z]{8,16}', str(password_1)) is None:
            return JsonResponse({'username': username, 'password': password_1, 'errno': 1002, 'msg': "密码格式错误"})
        if password_1 != password_2:
            return JsonResponse({'errno': 1003, 'msg': "两次输入的密码不同"})
        else:
            # 为用户分配不重复的uid
            uid = str(random.randint(10 ** 9, 10 ** 10 - 1))
            while User.objects.filter(uid=uid).exists():
                uid = str(random.randint(10 ** 9, 10 ** 10 - 1))
            # 数据库存取：新建 User 对象，赋值并保存
            new_user = User(uid=uid, username=username, password=password_1, email=email)
            new_user.save()  # 一定要save才能保存到数据库中
            return JsonResponse({'uid': uid, 'errno': 0, 'msg': "注册成功"})
    else:
        return JsonResponse({'error': 1, 'msg': "请求方式错误"})
        # return render(request, 'register.html', {})


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
            return JsonResponse({'errno': 1011, 'msg': "请先注册"})
        if user.password == password:  # 判断请求的密码是否与数据库存储的密码相同
            request.session['id'] = user.uid  # 密码正确则将用户名存储于session（django用于存储登录信息的数据库位置）
            return JsonResponse({'uid': user.uid, 'errno': 0, 'msg': "登录成功"})
        else:
            return JsonResponse({'errno': 1012, 'msg': "密码错误"})
    else:
        return JsonResponse({'error': 1, 'msg': "请求方式错误"})
        # return render(request, 'login.html', {})


@csrf_exempt
def logout(request):
    request.session.flush()
    return JsonResponse({'errno': 0, 'msg': "注销成功"})


@csrf_exempt
def display_profile(request):
    # 如果用户已登录，展示用户信息
    if request.session.get('id').exist():
        uid = request.session.get('id')
        user = User.objects.get(uid=uid)
        context = {
            'username': user.username,
            'uid': user.uid,
            'email': user.email,
            'avatar_url': user.avatar_url
        }
        return render(request, 'profile.html', context=context)
    # 若用户未登录，跳转到登录页面
    else:
        return render(request, 'login.html', {})


@csrf_exempt
def edit_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        avatar_url = request.POST.get('avatar_url')
        uid = request.session.get('id')
        user = User.objects.get(uid=uid)
        # if email != user.email:
        # 是否需要再次验证邮箱？
        user.username = username
        user.email = email
        user.avatar_url = avatar_url
        user.save()
    else:
        return render(request, 'edit_profile.html', {})


@csrf_exempt
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        password_1 = request.POST.get('password_1')
        password_2 = request.POST.get('password_2')
        uid = request.session.get('id')
        user = User.objects.get(uid=uid)
        if old_password != user.password:
            return JsonResponse({'errno': 1013, 'msg': "密码错误，请重新输入"})
        if re.match('(?!^[0-9]+$)(?!^[a-zA-Z]+$)[0-9A-Za-z]{8,16}', str(password_1)) is None:
            return JsonResponse({'password': password_1, 'errno': 1014, 'msg': "密码格式错误"})
        if password_1 != password_2:
            return JsonResponse({'errno': 1015, 'msg': "两次输入的密码不同"})
        user.password = password_1
        user.save()
        return JsonResponse({'errno': 0, 'msg': "密码修改成功"})
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方式错误"})


@csrf_exempt
def create_follow(request):
    if request.method == 'POST':
        following_id = request.POST.get('following_id')
        follower_id = request.session.get('id')
        now_time = time.time()
        follow = Follow(follower_id=follower_id, following_id=following_id, created_at=now_time)
        follow.save()
        resp = {'follower': follower_id, 'following': following_id, 'errno': 0, 'msg': '关注成功'}
        return JsonResponse(resp)
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方式错误"})


@csrf_exempt
def remove_follow(request):
    if request.method == 'POST':
        following_id = request.POST.get('following_id')
        follower_id = request.session.get('id')
        follow = Follow.objects.get(follower_id=follower_id, following_id=following_id)
        follow.delete()
        resp = {'follower': follower_id, 'following': following_id, 'errno': 0, 'msg': '取关成功'}
        return JsonResponse(resp)
    else:
        return JsonResponse({'errno': 1, 'msg': "请求方式错误"})


@csrf_exempt
def get_followings(request):
    following_list = []
    uid = request.session.get('id')
    followings = Follow.objects.filter(follower_id=uid)
    for following in followings:
        following_data = {
            'following_id': following.following_id,
            'follow_time': following.created_at
        }
        following_list.append(following_data)
    return JsonResponse({'errno': 0, 'msg': "关注列表查询成功", 'data': following_list})


@csrf_exempt
def get_followers(request):
    follower_list = []
    uid = request.session.get('id')
    followers = Follow.objects.filter(following_id=uid)
    for follower in followers:
        follower_data = {
            'following_id': follower.follower_id,
            'follow_time': follower.created_at
        }
        follower_list.append(follower_data)
    return JsonResponse({'errno': 0, 'msg': "粉丝列表查询成功", 'data': follower_list})
