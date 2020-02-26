from django.db import models


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
