# Generated by Django 3.2.9 on 2023-05-11 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comlpaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(verbose_name='投诉者ID')),
                ('video_id', models.IntegerField(verbose_name='被投诉的视频ID')),
                ('reason', models.CharField(max_length=255, verbose_name='投诉原因')),
                ('status', models.IntegerField(verbose_name='处理状态')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='投诉时间')),
            ],
        ),
    ]
