# Generated by Django 2.2.6 on 2020-02-29 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0016_auto_20200229_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='mark_score',
            field=models.IntegerField(default=5, verbose_name='活动评分'),
        ),
        migrations.AddField(
            model_name='simpleactivity',
            name='mark_score',
            field=models.IntegerField(default=5, verbose_name='活动评分'),
        ),
    ]