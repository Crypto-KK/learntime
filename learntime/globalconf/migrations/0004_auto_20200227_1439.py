# Generated by Django 2.2.6 on 2020-02-27 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('globalconf', '0003_auto_20200226_2121'),
    ]

    operations = [
        migrations.AddField(
            model_name='configration',
            name='database_host',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库地址'),
        ),
        migrations.AddField(
            model_name='configration',
            name='database_pass',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库密码'),
        ),
        migrations.AddField(
            model_name='configration',
            name='database_user',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='数据库用户'),
        ),
    ]