from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models

from learntime.utils.models import CreatedUpdatedMixin


class Configration(models.Model):
    """全局配置"""
    class Meta:
        verbose_name = "配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "全局配置"

    notice = models.TextField(verbose_name="系统公告", default="")
    maintenance_notice = models.TextField(verbose_name="维护提示", default="")
    is_maintenance = models.BooleanField(default=False, verbose_name="维护")
    criterion = models.FloatField(default=30, verbose_name="学时计算基准分数")
    default_password = models.CharField(max_length=20, verbose_name="管理员默认密码", default="123456")

    database_host = models.CharField(verbose_name="数据库地址", max_length=50, null=True, blank=True)
    database_user = models.CharField(verbose_name="数据库用户", max_length=50, null=True, blank=True)
    database_pass = models.CharField(verbose_name="数据库密码", max_length=50, null=True, blank=True)


class Help(CreatedUpdatedMixin, models.Model):
    """帮助文档"""
    category = models.CharField(max_length=50, verbose_name="分类名称", unique=True)
    title = models.CharField(max_length=50, verbose_name="标题")
    content = RichTextUploadingField(verbose_name="内容")

    class Meta:
        verbose_name = "帮助文档"
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['category'], name='category_idx')
        ]
