# Generated by Django 2.2.6 on 2020-02-28 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0013_activity_is_craft'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='is_craft',
            field=models.BooleanField(default=True, verbose_name='是否为草稿'),
        ),
    ]