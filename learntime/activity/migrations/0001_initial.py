# Generated by Django 2.2.6 on 2019-11-04 19:49

import datetime
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='活动id')),
                ('name', models.CharField(max_length=255, verbose_name='活动名称')),
                ('desc', models.TextField(verbose_name='描述')),
                ('score_player', models.FloatField(default=0, verbose_name='参与者学时')),
                ('score_staff', models.FloatField(default=0, verbose_name='工作人员学时')),
                ('score_viewer', models.FloatField(default=0, verbose_name='观众学时')),
                ('sponsor', models.CharField(max_length=255, verbose_name='组织方')),
                ('time', models.DateTimeField(default=datetime.datetime.now, verbose_name='活动时间')),
                ('is_verify', models.BooleanField(default=False, verbose_name='是否通过审核')),
            ],
            options={
                'verbose_name': '活动',
                'verbose_name_plural': '活动',
                'db_table': 'activity',
            },
        ),
    ]