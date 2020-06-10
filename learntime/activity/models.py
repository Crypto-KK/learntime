import uuid
from datetime import datetime

from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from django.db import models

from learntime.utils.models import CreatedUpdatedMixin

JOIN_TYPE = (
    (1, '参赛者'),
    (2, '观众'),
    (3, '工作人员'),
)


def upload_logo(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f'{uuid.uuid4().hex.__str__()}.{ext}'
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day
    return f"activity/logo/{year}/{month}/{day}/{new_filename}"


def upload_file(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f'{uuid.uuid4().hex.__str__()}.{ext}'
    year = datetime.now().year
    month = datetime.now().month
    day = datetime.now().day
    return f"activity/files/{year}/{month}/{day}/{new_filename}"


class Activity(CreatedUpdatedMixin, models.Model):
    """后台活动表"""

    TYPE = (
        ("n", "请选择"),
        ("fl_credit", "法律"),
        ("wt_credit", "文体"),
        ("xl_credit", "心理"),
        ("cxcy_credit", "创新创业"),
        ("sxdd_credit", "思想道德"),
    )


    uid = models.UUIDField(default=uuid.uuid4, primary_key=True,
                           editable=False, verbose_name="活动id")
    name = models.CharField(max_length=255, verbose_name="活动名称")
    # desc = UEditorField(verbose_name='活动内容', imagePath='activity/images/%Y/%m/%d/', width=800, height=350,
    #                     filePath='activity/files/%Y/%m/%d/', default='')
    logo = models.ImageField(upload_to=upload_logo, verbose_name="活动图标", null=True, blank=True)
    file = models.FileField(upload_to=upload_file, verbose_name="活动策划书",
                            null=True, blank=True, help_text="请上传.doc或者.docx后缀的文档")
    sponsor = models.CharField(verbose_name="主办方", max_length=255, null=True, blank=True)
    scope = models.CharField(max_length=255, verbose_name="允许报名的学院", default="全部")
    credit_type = models.CharField(choices=TYPE, max_length=20, verbose_name="学时类别",
                                   default="n", null=True, blank=True)
    place = models.CharField(max_length=255, verbose_name="活动地点", null=True, blank=True)
    time = models.CharField(verbose_name="活动时间", max_length=255, null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True, verbose_name="报名截止日期")
    desc = RichTextUploadingField(verbose_name="活动描述", null=True, blank=True)
    join_type = models.SmallIntegerField(default=2, verbose_name="参与身份", choices=JOIN_TYPE,
                                         null=True, blank=True)
    score = models.FloatField(default=0, verbose_name="学时", null=True, blank=True)
    nums = models.IntegerField(verbose_name="人数上限", null=True, blank=True, help_text="若无名额限制，请不要填写该内容")
    is_verify = models.BooleanField(verbose_name="是否通过审核", default=False)
    is_verifying = models.BooleanField(verbose_name="是否正在进行审核", default=True)
    reason = models.CharField(max_length=255, verbose_name="审核失败原因", default="")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             verbose_name="发布者", null=True, blank=True,
                             related_name="my_activities")
    to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             verbose_name="院级审核者", null=True, blank=True,
                           related_name="waiting_for_verify_activities")
    to_school = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             verbose_name="校级审核者", null=True, blank=True,
                           related_name="school_waiting_for_verify_activities")

    is_craft = models.BooleanField(verbose_name="是否为草稿", default=True)

    stop = models.BooleanField(verbose_name="是否截止", default=False)

    mark_score = models.IntegerField(verbose_name="活动评分", default=5)

    class Meta:
        verbose_name = "活动"
        verbose_name_plural = verbose_name
        db_table = "activity_backend"
        ordering = ('-created_at', )

    def __str__(self):
        return self.name


class SimpleActivity(models.Model):
    """活动表"""

    uid = models.UUIDField(primary_key=True, verbose_name="活动id")
    name = models.CharField(max_length=255, verbose_name="活动名称",
                            null=True, blank=True)
    description = models.TextField(verbose_name="描述", null=True, blank=True)
    join_type = models.SmallIntegerField(default=2, verbose_name="参与身份", choices=JOIN_TYPE)
    score = models.FloatField(default=0, verbose_name="学时")
    sponsor = models.CharField(verbose_name="主办方", max_length=255,
                               null=True, blank=True)
    scope = models.CharField(max_length=255, verbose_name="允许报名的学院", default="全部")
    time = models.CharField(verbose_name="活动时间", max_length=255,
                            null=True, blank=True)
    stop = models.BooleanField(verbose_name="是否截止", default=False,
                               null=True, blank=True)
    nums = models.IntegerField(verbose_name="参加人数", null=True, blank=True)
    place = models.CharField(max_length=255, verbose_name="活动地点", default="",
                             null=True, blank=True)
    logo = models.CharField(verbose_name="活动图标", max_length=255, null=True, blank=True)
    credit_type = models.CharField(max_length=255, verbose_name="学时类别",
                                   null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True, verbose_name="报名截止日期")
    created = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='创建时间',
                                      blank=True, null=True)
    mark_score = models.IntegerField(verbose_name="活动评分", default=5)
    class Meta:
        verbose_name = "活动"
        verbose_name_plural = verbose_name
        db_table = "activity"
        ordering = ('-stop', )

    def __str__(self):
        return self.name



