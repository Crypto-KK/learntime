from django.conf import settings
from django.db import models
from django.db.models import DateTimeField

from ckeditor_uploader.fields import RichTextUploadingField

from learntime.utils.models import CreatedUpdatedMixin
from learntime.activity.models import Activity
from learntime.student.models import Student


class StudentActivity(models.Model):
    """
    学生活动关联表
    """
    JOIN_TYPE = (
        (1, '参赛者'),
        (2, '观众'),
        (3, '工作人员'),
    )
    STATUS = (
        (1, '报名'),
        (2, '签到成功'),
        (3, '签退成功'),
    )
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING,
                                verbose_name="学生", related_name="join_activities")
    student_name = models.CharField(max_length=20, verbose_name="姓名", null=True, blank=True)
    academy = models.CharField(max_length=20, verbose_name="学院", null=True, blank=True)
    grade = models.CharField(max_length=20, verbose_name="年级", null=True, blank=True)
    clazz = models.CharField(max_length=20, verbose_name="班级", null=True, blank=True)

    activity_name = models.CharField(max_length=50, verbose_name="活动名称", null=True, blank=True)
    activity = models.ForeignKey(Activity, on_delete=models.DO_NOTHING,
                                 verbose_name="活动", null=True, blank=True,
                                 related_name="join_students")
    credit = models.FloatField(default=0, verbose_name="获得学时")
    credit_type = models.CharField(max_length=20, verbose_name="学时类别", default="")
    create_time = DateTimeField(db_index=True, auto_now_add=True,
                                verbose_name='创建时间')
    join_type = models.SmallIntegerField(verbose_name="参与类型", choices=JOIN_TYPE)
    status = models.SmallIntegerField(verbose_name="参与状态", default=1, choices=STATUS)


    class Meta:
        verbose_name = "学生活动表"
        verbose_name_plural = verbose_name
        db_table = "student_activities"
        ordering = ("-create_time", )


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


class Comment(CreatedUpdatedMixin, models.Model):
    """评论表"""
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name="活动",
                                 related_name="comments")
    student_id = models.CharField(verbose_name="学号", max_length=20)
    student_name = models.CharField(verbose_name="姓名", max_length=20)
    student_class = models.CharField(verbose_name="班级", max_length=20)
    student_grade = models.CharField(verbose_name="年级", max_length=20)
    student_academy = models.CharField(verbose_name="学院", max_length=20)
    score = models.IntegerField(verbose_name="评论分数", default=5)
    content = models.CharField(max_length=255, verbose_name="内容")

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['student_id'], name='student_id_idx')
        ]
        db_table = "comment"
        ordering = ('-created_at',)

    def __str__(self):
        return self.content


class FeedBack(CreatedUpdatedMixin, models.Model):
    """反馈"""
    email = models.EmailField(verbose_name="反馈人邮箱")
    name = models.CharField(verbose_name="反馈人姓名", max_length=20)
    content = RichTextUploadingField(verbose_name="内容")
    is_fix = models.BooleanField(default=False, verbose_name="是否解决")
    reply = models.CharField(max_length=255, verbose_name="回复", default="")

    class Meta:
        verbose_name = "反馈"
        verbose_name_plural = verbose_name
        ordering = ('-created_at',)
        db_table = "feedback"

