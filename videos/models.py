import os
from django.db import models

from accounts.models import User

# Create your models here.
class Video(models.Model):
    label=models.CharField(verbose_name="标签",default="娱乐",max_length=255)
    title=models.CharField(verbose_name='视频标题',max_length=255)
    description=models.CharField(verbose_name='视频描述',max_length=255)

    # 这里的字段建议设置上默认值
    video_url = models.CharField(verbose_name='视频路径', max_length=128, default='')
    cover_url = models.CharField(verbose_name='封面路径', max_length=128, default='')

    user_id=models.IntegerField(verbose_name='所属用户',null=True)
    created_at=models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    reviewed_at=models.DateTimeField(verbose_name='审核时间',null=True)
    reviewed_status=models.IntegerField(verbose_name='审核状态',default=0) #0未审核 1审核通过 2需复核

    view_amount=models.IntegerField(verbose_name='播放量',default=0)
    fav_amount=models.IntegerField(verbose_name='收藏量',default=0)
    like_amount=models.IntegerField(verbose_name='点赞数',default=0)
    class Meta:
        app_label = 'videos'
    def to_dict(self):
        return {
            'id':self.id,
            'label':self.label,
            'title':self.title,
            'description':self.description,
            'video_url': self.video_url,
            'cover_url': self.cover_url,
            'user':self.user_id,
            'created_at':self.created_at,
            'reviewed_at':self.reviewed_at,
            'reviewed_status':self.reviewed_status,
            'view_amount':self.view_amount,
            'fav_amount':self.fav_amount,
            'like_amount':self.like_amount,
        }
    
class Like(models.Model):
    user_id=models.IntegerField(verbose_name='点赞者ID',null=True )
    video_id=models.IntegerField(verbose_name='被点赞的视频ID',null=True )
    created_at=models.DateTimeField(verbose_name='点赞时间', auto_now_add=True)
    class Meta:
        app_label = 'videos'


class Comment(models.Model):
    user_id = models.IntegerField(verbose_name='评论者ID' ,null=True)
    video_id = models.IntegerField(verbose_name='被评论的视频ID',null=True )
    content=models.CharField(verbose_name='评论内容',max_length=255)
    created_at = models.DateTimeField(verbose_name='评论时间',auto_now_add=True)
    class Meta:
        app_label = 'videos'
    def to_dict(self):
        return {
            'user_id':self.user_id,
            'video_id':self.video_id,
            'content':self.content,
            'created_at':self.created_at
        }

class Reply(models.Model):
    #id = models.IntegerField(verbose_name='回复ID',primary_key=True )
    user_id = models.IntegerField(verbose_name='回复者ID',null=True )
    comment_id = models.IntegerField(verbose_name='所属评论ID',null=True )
    content=models.CharField(verbose_name='回复内容',max_length=255)
    created_at = models.DateTimeField(verbose_name='回复时间', auto_now_add=True)
    class Meta:
        app_label = 'videos'
    def to_dict(self):
        return {
            'user_id':self.user_id,
            'comment_id':self.comment_id,
            'content':self.content,
            'created_at':self.created_at
        }

class Favorite(models.Model):
    title = models.CharField(verbose_name='默认收藏夹', max_length=64)
    description = models.TextField(verbose_name='描述')
    status = models.IntegerField(verbose_name="是否为私有", default=0)  # 0 - 公开    1 - 私有
    #user = models.ForeignKey(User, verbose_name='收藏夹所属用户', on_delete=models.CASCADE)
    user_id = models.IntegerField(verbose_name='收藏者ID',null=True )
    #avatar_url = models.CharField(verbose_name='封面路径', max_length=128)
    def to_dict(self):
        return {
            'title':self.title,
            'description':self.description,
            'status':self.status,
            'user_id':self.user_id
        }
class Favlist(models.Model):
    favorite_id = models.IntegerField(verbose_name='收藏夹编号', default=0)
    video_id = models.IntegerField(verbose_name='收藏视频ID',null=True )

    def to_dict(self):
        return {
            'favorite_id':self.favorite_id,
            'video_id':self.video_id,
        }
