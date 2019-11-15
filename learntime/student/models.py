from django.db import models

from learntime.utils.models import CreatedUpdatedMixin


class Student(CreatedUpdatedMixin, models.Model):
    """学生表"""
    uid = models.CharField(max_length=255, primary_key=True,
                           verbose_name="学号", help_text="学号")
    name = models.CharField(max_length=255, verbose_name="姓名")
    grade = models.CharField(max_length=255, null=True, blank=True,
                             verbose_name="年级")
    academy = models.CharField(max_length=255, null=True, blank=True,
                               verbose_name="学院")
    clazz = models.CharField(max_length=255, null=True, blank=True,
                             verbose_name="班级")
    credit = models.FloatField(default=0, verbose_name="学时")
    cxcy_credit = models.FloatField(default=0, verbose_name="创新创业学时")
    sxdd_credit = models.FloatField(default=0, verbose_name="思想道德学时")
    fl_credit = models.FloatField(default=0, verbose_name="法律学时")
    wt_credit = models.FloatField(default=0, verbose_name="文体学时")
    xl_credit = models.FloatField(default=0, verbose_name="心理学时")

    class Meta:
        verbose_name = "学生"
        verbose_name_plural = verbose_name
        db_table = "student_backend"
        ordering = ('-credit',)

    def __str__(self):
        return self.uid


class StudentFile(models.Model):
    excel_file = models.FileField(upload_to="student/%Y/%m/%d/", verbose_name="学生文件")

    class Meta:
        verbose_name = "学生excel文件"
        verbose_name_plural = verbose_name
        db_table = "student_file"


