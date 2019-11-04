import uuid
from datetime import datetime

from django.db import models

from learntime.utils.models import CreatedUpdatedMixin


class Activity(CreatedUpdatedMixin, models.Model):
    """活动表"""
    uid = models.UUIDField(default=uuid.uuid4, primary_key=True,
                           editable=False, verbose_name="活动id")
    name = models.CharField(max_length=255, verbose_name="活动名称")
    desc = models.TextField(verbose_name="描述")
    score_player = models.FloatField(default=0, verbose_name="参与者学时")
    score_staff = models.FloatField(default=0, verbose_name="工作人员学时")
    score_viewer = models.FloatField(default=0, verbose_name="观众学时")
    sponsor = models.CharField(verbose_name="组织方", max_length=255)
    time = models.DateTimeField(default=datetime.now, verbose_name="活动时间")
    is_verify = models.BooleanField(verbose_name="是否通过审核", default=False)

    class Meta:
        verbose_name = "活动"
        verbose_name_plural = verbose_name
        db_table = "activity"


    def __str__(self):
        return self.name
