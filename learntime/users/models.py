from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, IntegerField, Model, BooleanField, ForeignKey, Q
from django.urls import reverse
from django.db import models

from learntime.utils.models import CreatedUpdatedMixin


class User(AbstractUser):
    IDENTITY = (
        (1, '超级管理员'), #最高权限
        (2, '校级'), #校级
        (3, '院级'), #院级
        (4, '学生干部级'), #干部级
        (5, '组织账号')
    )

    name = CharField(verbose_name="姓名", max_length=20)
    academy = CharField(verbose_name='学院', max_length=20, null=True, blank=True)
    grade = CharField(verbose_name='年级', max_length=20, null=True, blank=True,
                      help_text="请按照格式填写，例如(2019级)")
    klass = CharField(verbose_name='班级', max_length=20, null=True, blank=True,
                      help_text="填写格式按照格式填写，例如(软件工程1班)")
    department = CharField(verbose_name="部门", max_length=50, null=True, blank=True)
    organization = CharField(verbose_name="社团协会", max_length=50, null=True, blank=True)
    role = IntegerField(verbose_name="权限", choices=IDENTITY, default=4)
    is_freeze = BooleanField(verbose_name="是否冻结", default=False)
    is_delete = BooleanField(verbose_name="是否删除", default=False)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def __str__(self):
        return self.name

    def register(self):
        """用户注册，后台需要审核"""
        self.is_active = False
        self.save()

    def register_success(self):
        """用户通过审核，注册成功"""
        self.is_active = True
        self.save()

    class Meta:
        verbose_name = "管理员"
        verbose_name_plural = verbose_name
        ordering = ('role', )


class AcademyManager(models.Manager):
    """将'全部'学院隐藏掉"""
    def all(self):
        return super().filter(~Q(name="全部"))


class Academy(Model):
    """学院数据库"""
    name = CharField(max_length=50, verbose_name="学院名称")
    objects = AcademyManager()
    def __str__(self):
        return self.name

    class Meta:
        db_table = "academy"



class Grade(Model):
    """年级数据库"""
    name = CharField(max_length=20, verbose_name="年级")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "grade"
