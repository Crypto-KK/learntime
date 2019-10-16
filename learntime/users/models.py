from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, IntegerField
from django.urls import reverse
from django.utils.functional import cached_property
from django.db import models

from learntime.users.enums import UserEnum
from learntime.utils.models import CreatedUpdatedMixin


class User(AbstractUser):
    IDENTITY = (
        (1, 'root'), #最高权限
        (2, '校级'), #校级
        (3, '学院级'), #院级
        (4, '干部级'), #干部级
    )

    name = CharField(verbose_name="姓名", max_length=20)
    academy = CharField(verbose_name='学院', max_length=20, null=True, blank=True)
    grade = CharField(verbose_name='年级', max_length=20, null=True, blank=True)
    klass = CharField(verbose_name='班级', max_length=20, null=True, blank=True)
    identity = IntegerField(verbose_name='身份', choices=IDENTITY, default=1)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    @cached_property
    def get_name(self):
        """获取用户姓名"""
        return self.name

    @cached_property
    def get_identity(self):
        """获取用户身份"""
        return self.identity

    def __str__(self):
        return self.username

    def switch_level_to_root(self):
        """切换到管理员"""
        self.identity = UserEnum.ROOT.value
        self.save()

    def switch_level_to_school(self):
        """切换到校级管理员"""
        self.identity = UserEnum.SCHOOL.value
        self.save()

    def switch_level_to_academy(self):
        """切换到院级管理员"""
        self.identity = UserEnum.ACADEMY.value
        self.save()

    def switch_level_to_student(self):
        """切换到干部级管理员"""
        self.identity = UserEnum.STUDENT.value
        self.save()

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
