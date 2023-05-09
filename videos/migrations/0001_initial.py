# Generated by Django 3.2.9 on 2023-05-09 11:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0002_vcode'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collect',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(verbose_name='收藏者ID')),
                ('video_id', models.IntegerField(verbose_name='被收藏的视频ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=255, verbose_name='评论内容')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='评论时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.user', verbose_name='评论的用户')),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(default='娱乐', max_length=255, verbose_name='标签')),
                ('title', models.CharField(max_length=255, verbose_name='视频标题')),
                ('description', models.CharField(max_length=255, verbose_name='视频描述')),
                ('video_path', models.CharField(max_length=255, null=True, verbose_name='视频地址')),
                ('cover_path', models.CharField(max_length=255, null=True, verbose_name='封面地址')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('reviewed_at', models.DateTimeField(null=True, verbose_name='审核时间')),
                ('reviewed_status', models.IntegerField(default=0, verbose_name='审核状态')),
                ('view_amount', models.IntegerField(default=0, verbose_name='播放量')),
                ('fav_amount', models.IntegerField(default=0, verbose_name='收藏量')),
                ('like_amount', models.IntegerField(default=0, verbose_name='点赞数')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.user', verbose_name='所属用户')),
            ],
        ),
        migrations.CreateModel(
            name='Reply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=255, verbose_name='回复内容')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='回复时间')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='videos.comment', verbose_name='评论所属用户')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.user', verbose_name='回复的用户')),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.user', verbose_name='点赞的用户')),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='videos.video', verbose_name='点赞的视频')),
            ],
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=64, verbose_name='默认收藏夹')),
                ('description', models.TextField(verbose_name='描述')),
                ('status', models.IntegerField(default=0, verbose_name='是否为私有')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.user', verbose_name='收藏夹所属用户')),
            ],
        ),
        migrations.CreateModel(
            name='Favlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('favorite_id', models.IntegerField(default=0, verbose_name='收藏夹编号')),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='videos.video', verbose_name='')),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='videos.video', verbose_name='评论的视频'),
        ),
    ]
