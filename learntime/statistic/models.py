import uuid

from django.db import models


class CreditStat(models.Model):
    """学时统计表，每月统计一次"""
    key = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, verbose_name="活动id")
    uid = models.CharField(max_length=255, verbose_name="学号")
    name = models.CharField(max_length=255, verbose_name="姓名")
    grade = models.CharField(max_length=255, default="", verbose_name="年级")
    academy = models.CharField(max_length=255, default="", verbose_name="学院")
    clazz = models.CharField(max_length=255, default="", verbose_name="班级")
    credit = models.FloatField(default=0, verbose_name="学时")
    cxcy_credit = models.FloatField(default=0, verbose_name="创新创业学时")
    sxdd_credit = models.FloatField(default=0, verbose_name="思想道德学时")
    fl_credit = models.FloatField(default=0, verbose_name="法律学时")
    wt_credit = models.FloatField(default=0, verbose_name="文体学时")
    xl_credit = models.FloatField(default=0, verbose_name="心理学时")
    record_time = models.DateField(verbose_name="统计时间")

    def __str__(self):
        return f"{self.uid} of {self.record_time}"

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """校准总学时"""
        self.credit = self.cxcy_credit + self.sxdd_credit + self.fl_credit + \
                      self.wt_credit + self.xl_credit
        super(CreditStat, self).save(force_insert=False, force_update=False, using=None,
             update_fields=None)

    class Meta:
        verbose_name = "学时统计表"
        verbose_name_plural = verbose_name
        db_table = "credit_stat"
        indexes = [
            models.Index(fields=['uid'], name='uid_idx')
        ]

