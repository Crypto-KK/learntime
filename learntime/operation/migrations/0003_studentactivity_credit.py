# Generated by Django 2.2.6 on 2020-01-18 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operation', '0002_studentactivity_student_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentactivity',
            name='credit',
            field=models.FloatField(default=0, verbose_name='获得学时'),
        ),
    ]
