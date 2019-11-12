from django.conf import settings
from django.db import models
from django.db.models import DateTimeField

from learntime.activity.models import Activity
from learntime.student.models import Student


class StudentActivity(models.Model):

    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING,
                                verbose_name="学生")
    activity = models.ForeignKey(Activity, on_delete=models.DO_NOTHING,
                                 verbose_name="活动")
    create_time = DateTimeField(db_index=True, auto_now_add=True,
                                verbose_name='创建时间')
    join_type = models.CharField(max_length=255, verbose_name="参与类型")


    class Meta:
        verbose_name = "学生活动表"
        verbose_name_plural = verbose_name
        db_table = "student_activities"


class Log(models.Model):
    """操作日志"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             verbose_name="操作者", related_name="my_logs")
    content = models.TextField(verbose_name="内容")
    created_at = models.DateTimeField(db_index=True, auto_now_add=True,
                                      verbose_name='创建时间')

    class Meta:
        verbose_name = "日志"
        verbose_name_plural = verbose_name
        db_table = "log"
        ordering = ('-created_at',)

    def __str__(self):
        return self.content
