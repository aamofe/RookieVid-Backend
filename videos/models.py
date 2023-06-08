import os
from datetime import timedelta, timezone

import pytz
from django.db import models

from accounts.models import User, Follow
shanghai_tz = pytz.timezone('Asia/Shanghai')

class Like(models.Model):
    user_id=models.IntegerField(verbose_name='点赞者ID',null=True )
    video_id=models.IntegerField(verbose_name='被点赞的视频ID',null=True )
    created_at=models.DateTimeField(verbose_name='点赞时间', auto_now_add=True)
    class Meta:
        app_label = 'videos'
    def to_dict(self):
        created_at_shanghai = (self.created_at.astimezone(shanghai_tz)).strftime('%Y-%m-%d %H:%M:%S')
        return {
            'id':self.id,
            'user_id':self.user_id,
            'video_id':self.video_id,
            'created_at':created_at_shanghai,
        }

class Favlist(models.Model):
    favorite_id = models.IntegerField(verbose_name='收藏夹编号', default=0)
    video_id = models.IntegerField(verbose_name='收藏视频ID',null=True )
    created_at = models.DateTimeField(verbose_name='收藏视频时间', null=True,auto_now_add=True)
    user_id = models.IntegerField(verbose_name='所属用户', null=True)
    def to_dict(self):
        return {
            'id':self.id,
            'favorite_id':self.favorite_id,
            'video_id':self.video_id,
        }
# Create your models here.
class Video(models.Model):
    label=models.CharField(verbose_name="标签",default="娱乐",max_length=255)
    title=models.CharField(verbose_name='视频标题',max_length=255)
    description=models.CharField(verbose_name='视频描述',max_length=255)
    JobId=models.CharField(verbose_name='腾讯云自动审核ID',null=True,max_length=255)
    # 这里的字段建议设置上默认值
    video_url = models.CharField(verbose_name='视频路径', max_length=128, default='')
    cover_url = models.CharField(verbose_name='封面路径', max_length=128, default='')

    user_id=models.IntegerField(verbose_name='所属用户',null=True)
    created_at=models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    reviewed_at=models.DateTimeField(verbose_name='审核时间',null=True)
    reviewed_status=models.IntegerField(verbose_name='审核状态',default=0) #0未审核 1审核通过 2需复核

    view_amount=models.IntegerField(verbose_name='播放量',default=0)
    like_amount=models.IntegerField(verbose_name='点赞数',default=0)
    class Meta:
        app_label = 'videos'
    def to_simple_dict(self):
        try:
            user=User.objects.get(id=self.user_id)
        except User.DoesNotExist:
            user=User.objects.get(id=16)
        fav_amount = len(Favlist.objects.filter(video_id=self.id).values('user_id').distinct())
        created_at_shanghai = (self.created_at.astimezone(shanghai_tz)).strftime('%Y-%m-%d %H:%M:%S')
        #aacover_url=self.cover_url.replace("https://aamofe-1315620690.cos.ap-beijing.myqcloud.com", "http://aamofe.top")
        #aavideo_url=self.video_url.replace("https://aamofe-1315620690.cos.ap-beijing.myqcloud.com", "http://aamofe.top")
        return {
            'id': self.id,
            'label': self.label,
            'title': self.title,
            'description': self.description,
            #'video_url':aavideo_url,
            'video_url': self.video_url,
            #'cover_url': aacover_url,
            'cover_url': self.cover_url,
            'created_at': created_at_shanghai,
            'reviewed_at': self.reviewed_at,
            'reviewed_status': self.reviewed_status,
            'view_amount': self.view_amount,
            'user_id':user.id,
            'fav_amount':fav_amount,
            'like_amount': self.like_amount,
            'user_name': user.username,
        }
    def to_dict(self):
        try:
            user=User.objects.get(id=self.user_id)
        except User.DoesNotExist:
            user=User.objects.get(id=16)
        fav_amount = len(Favlist.objects.filter(video_id=self.id).values('user_id').distinct())
        follower=Follow.objects.filter(following_id=user.id)
        created_at_shanghai = (self.created_at.astimezone(shanghai_tz)).strftime('%Y-%m-%d %H:%M:%S')
        # aacover_url=self.cover_url.replace("https://aamofe-1315620690.cos.ap-beijing.myqcloud.com", "http://aamofe.top")
        # aavideo_url=self.video_url.replace("https://aamofe-1315620690.cos.ap-beijing.myqcloud.com", "http://aamofe.top")
        #print("aaa : ",aacover_url)
        return {
            'id':self.id,
            'label':self.label,
            'title':self.title,
            'description':self.description,
            #'video_url':aavideo_url,
            'video_url': self.video_url,
            #'cover_url': aacover_url,
            'cover_url': self.cover_url,
            'created_at':created_at_shanghai,
            'reviewed_at':self.reviewed_at,
            'reviewed_status':self.reviewed_status,
            'view_amount':self.view_amount,
            'fav_amount':fav_amount,
            'like_amount':self.like_amount,
            'user_id': self.user_id,
            'user_name': user.username,
            'avatar_url':user.avatar_url,
            'user_description':user.signature,
            'follower_amount':len(follower),
        }
    



class Comment(models.Model):
    user_id = models.IntegerField(verbose_name='评论者ID' ,null=True)
    video_id = models.IntegerField(verbose_name='被评论的视频ID',null=True )
    content=models.CharField(verbose_name='评论内容',max_length=255)
    created_at = models.DateTimeField(verbose_name='评论时间',auto_now_add=True)
    comment_id= models.IntegerField(verbose_name='回复的评论ID' ,default=0,null=True)#0表示为评论，其他表示为回复
    class Meta:
        app_label = 'videos'
    def to_dict(self):
        created_at_shanghai = (self.created_at.astimezone(shanghai_tz)).strftime('%Y-%m-%d %H:%M:%S')
        try:
            user=User.objects.get(id=self.user_id)
        except User.DoesNotExist:
            user=User.objects.get(id=16)
        return {
            'id': self.id,
            #'comment_id': self.comment_id,
            'user_id': user.id,
            'user_name': user.username,
            'avatar_url': user.avatar_url,
            'video_id': self.video_id,
            'content': self.content,
            'created_at': created_at_shanghai,
            'reply':[],
            'reply_amount':0,
        }

class Reply(models.Model):
    #id = models.IntegerField(verbose_name='回复ID',primary_key=True )
    user_id = models.IntegerField(verbose_name='回复者ID',null=True )
    comment_id = models.IntegerField(verbose_name='所属评论ID',null=True )
    video_id = models.IntegerField(verbose_name='被回复的视频ID',default=1, null=True)
    content=models.CharField(verbose_name='回复内容',max_length=255)
    created_at = models.DateTimeField(verbose_name='回复时间', auto_now_add=True)
    class Meta:
        app_label = 'videos'
    def to_dict(self):
        created_at_shanghai = (self.created_at.astimezone(shanghai_tz)).strftime('%Y-%m-%d %H:%M:%S')
        return {
            'id': self.id,
            'user_id':self.user_id,
            'video_id':self.video_id,
            'user_name':User.objects.get(id=self.user_id).username,
            'avatar_url':User.objects.get(id=self.user_id).avatar_url,
            'comment_id':self.comment_id,
            'content':self.content,
            'created_at':created_at_shanghai,
        }

class Favorite(models.Model):
    title = models.CharField(verbose_name='默认收藏夹', max_length=64)
    description = models.TextField(verbose_name='描述')
    is_private = models.IntegerField(verbose_name="是否为私有", default=0)  # 0 - 公开    1 - 私有
    #user = models.ForeignKey(User, verbose_name='收藏夹所属用户', on_delete=models.CASCADE)
    user_id = models.IntegerField(verbose_name='收藏者ID',null=True )
    cover_url = models.CharField(verbose_name='封面路径', default='https://aamofe-1315620690.cos.ap-beijing.myqcloud.com/favorite_cover/0.png',max_length=128)
    created_at = models.DateTimeField(verbose_name='创建收藏夹时间',null=True, auto_now_add=True)
    def to_dict(self):
        created_at_shanghai = (self.created_at.astimezone(shanghai_tz)).strftime('%Y-%m-%d %H:%M:%S')
        return {
            'id':self.id,
            'title':self.title,
            'description':self.description,
            'is_private':self.is_private,
            'user_id':self.user_id,
            'cover_url':self.cover_url,
            'created_at:':created_at_shanghai,
        }


class History(models.Model):
    user_id = models.IntegerField(verbose_name='播放记录所有者',null=True )
    video_id = models.IntegerField(verbose_name='观看的视频ID',default=1, null=True)
    created_at = models.DateTimeField(verbose_name='观看的时间', auto_now_add=True)
    def to_dict(self):
        created_at_shanghai = (self.created_at.astimezone(shanghai_tz)).strftime('%Y-%m-%d %H:%M:%S')
        video=Video.objects.get(id=self.video_id)
        user=User.objects.get(id=video.user_id)
        return{
            'id':self.id,
            'video':video.to_simple_dict(),
            'user_name':user.username,
            'user_id':user.id,
            'avatar_url':user.avatar_url,
            'created_at':created_at_shanghai,
        }