# Generated by Django 2.2.6 on 2019-11-06 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0008_auto_20191105_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='wt_credit',
            field=models.FloatField(default=0, verbose_name='文体学时'),
        ),
    ]