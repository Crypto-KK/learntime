# Generated by Django 2.2.6 on 2020-09-24 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0008_auto_20200617_1701'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentcreditverify',
            name='year',
            field=models.CharField(default='', max_length=50, verbose_name='所属年度'),
        ),
    ]