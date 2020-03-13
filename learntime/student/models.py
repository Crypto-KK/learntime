from django.contrib.auth import get_user_model
from django.db import models

from learntime.utils.models import CreatedUpdatedMixin


User = get_user_model()


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

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """总学时校准"""
        self.credit = float(self.cxcy_credit + self.sxdd_credit + self.fl_credit + self.wt_credit + self.xl_credit)
        super().save(force_insert=False, force_update=False, using=None,
             update_fields=None)


class StudentFile(models.Model):
    """学生导入的文件表"""
    excel_file = models.FileField(upload_to="student/%Y/%m/%d/", verbose_name="请选择文件")

    class Meta:
        verbose_name = "学生excel文件"
        verbose_name_plural = verbose_name
        db_table = "student_file"


class SimpleStudent(models.Model):
    """学生表"""
    uid = models.CharField(max_length=255, primary_key=True,
                           verbose_name="学号", help_text="学号")
    name = models.CharField(max_length=255, verbose_name="姓名")
    password = models.CharField(max_length=255, verbose_name="密码")
    email = models.CharField(max_length=50, verbose_name="邮箱", default='')
    grade = models.CharField(max_length=255, null=True, blank=True,
                             verbose_name="年级")
    academy = models.CharField(max_length=255, null=True, blank=True,
                               verbose_name="学院")
    clazz = models.CharField(max_length=255, null=True, blank=True,
                             verbose_name="班级")
    credit = models.FloatField(default=0, verbose_name="学时",
                               null=True, blank=True)
    cxcy_credit = models.FloatField(default=0, verbose_name="创新创业学时",
                                    null=True, blank=True)
    sxdd_credit = models.FloatField(default=0, verbose_name="思想道德学时",
                                    null=True, blank=True)
    fl_credit = models.FloatField(default=0, verbose_name="法律学时",
                                  null=True, blank=True)
    wt_credit = models.FloatField(default=0, verbose_name="文体学时",
                                  null=True, blank=True)
    xl_credit = models.FloatField(default=0, verbose_name="心理学时",
                                  null=True, blank=True)

    class Meta:
        verbose_name = "学生"
        verbose_name_plural = verbose_name
        db_table = "student"
        ordering = ('-credit',)

    def __str__(self):
        return self.uid


class StudentCreditVerify(models.Model):
    """使用excel表格导入需要批量加学时的学时名单
    例如：
        学号   姓名   加学时数
        001   测试      2
        002   儿子      2
    """
    CREDIT_TYPE = (
        (0, '未选择'),
        (1, '法律学时'),
        (2, '文体学时'),
        (3, '心理学时'),
        (4, '创新创业学时'),
        (5, '思想道德学时'),
    )
    activity_name = models.CharField(max_length=50, verbose_name="活动名称")
    sponsor = models.CharField(max_length=20, verbose_name="主办方")
    uid = models.CharField(max_length=20, verbose_name="学号")
    name = models.CharField(max_length=20, verbose_name="姓名")
    academy = models.CharField(max_length=20, verbose_name="学院")
    clazz = models.CharField(max_length=20, verbose_name="班级")
    join_type = models.CharField(max_length=20, verbose_name="参加类型")
    award = models.CharField(max_length=20, verbose_name="获奖情况")
    credit_type = models.CharField(max_length=20, verbose_name='认定项目')
    credit = models.FloatField(default=0, verbose_name="认定活动时")
    contact = models.CharField(max_length=50, verbose_name='填报人及联系方式')
    to_name = models.CharField(max_length=20, verbose_name='审核人')
    remark = models.CharField(max_length=50, verbose_name='备注', null=True, blank=True)
    user = models.ForeignKey(User, verbose_name="填写学时补录的管理员", on_delete=models.CASCADE,
                           related_name="applying_to_verify_credits")
    to = models.ForeignKey(User, verbose_name="审核者", on_delete=models.CASCADE,
                           related_name="waiting_to_verify_credits")
    verify = models.BooleanField(default=False, verbose_name="是否审核")
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return f'{self.user.name}请求给学生{self.uid}补录学时'

    class Meta:
        verbose_name = "请求加学时"
        verbose_name_plural = verbose_name
        db_table = "student_credit_verify"
        ordering = ('created_at',)
