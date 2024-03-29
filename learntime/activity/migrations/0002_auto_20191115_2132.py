# Generated by Django 2.2.6 on 2019-11-15 21:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('activity', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='waiting_for_verify_activities', to=settings.AUTH_USER_MODEL, verbose_name='院级审核者'),
        ),
        migrations.AddField(
            model_name='activity',
            name='to_school',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='school_waiting_for_verify_activities', to=settings.AUTH_USER_MODEL, verbose_name='校级审核者'),
        ),
        migrations.AddField(
            model_name='activity',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='my_activities', to=settings.AUTH_USER_MODEL, verbose_name='发布者'),
        ),
    ]
