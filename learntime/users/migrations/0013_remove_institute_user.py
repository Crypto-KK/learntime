# Generated by Django 2.2.6 on 2020-06-08 23:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20200608_2231'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='institute',
            name='user',
        ),
    ]
