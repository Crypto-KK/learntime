# Generated by Django 2.2.6 on 2020-04-12 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0017_auto_20200229_2146'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='scope',
            field=models.CharField(default='全部', max_length=255, verbose_name='允许报名的学院'),
        ),
        migrations.AddField(
            model_name='simpleactivity',
            name='scope',
            field=models.CharField(default='全部', max_length=255, verbose_name='允许报名的学院'),
        ),
    ]
