# Generated by Django 2.2.6 on 2019-11-20 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0005_auto_20191117_1429'),
    ]

    operations = [
        migrations.AddField(
            model_name='simpleactivity',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, null=True, verbose_name='创建时间'),
        ),
    ]
