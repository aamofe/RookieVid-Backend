# Generated by Django 3.2.9 on 2023-05-05 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='like',
            field=models.IntegerField(default=0, verbose_name='点赞数'),
        ),
    ]
