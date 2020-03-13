import json

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.base import View
from pyecharts.charts import Bar
from pyecharts.globals import ThemeType

from learntime.globalconf.models import Configration
from learntime.activity.models import Activity
from learntime.student.models import Student
from learntime.users.enums import RoleEnum
from learntime.utils.echarts_utils import EchartsResponse
from pyecharts import options as opts


User = get_user_model()

def rank_chart_view(request, maximum):
    """学时排名统计"""

    if maximum > 20:
        maximum = 20
    students = Student.objects.all()[:maximum]

    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            .add_xaxis([student.name for student in students])
            .add_yaxis("总学时", [student.credit for student in students])
            .set_global_opts(title_opts=opts.TitleOpts(title="学时排名TOP 15"))
            .set_colors(['#60acfc', '#5bc49f', '#ff7c7c'])
            .dump_options_with_quotes()
    )
    return EchartsResponse(json.loads(c))


class IndexView(LoginRequiredMixin, View):
    """首页视图"""
    def get(self, request):
        context = {
            "student_nums": Student.objects.count(),
            "activity_nums": Activity.objects.count(),
            "notice": Configration.objects.first().notice
        }
        role = request.user.role
        if role == RoleEnum.ROOT.value:
            # root能看到管理员数量和等待审核的管理员数量
            context.update({
                "admin_nums": User.objects.filter(is_active=True).count(),
                "verifying_admin_nums": User.objects.filter(is_active=False).count()
            })
        elif role == RoleEnum.SCHOOL.value:
            # 学校级管理员能看到等待自己审核的活动数量
            context.update({
                "verifying_activities_nums": request.user.school_waiting_for_verify_activities.count()
            })

        elif role == RoleEnum.ACADEMY.value:
            # 学院管理员能看到等待自己审核的活动数量
            context.update({
                "verifying_activities_nums": request.user.waiting_for_verify_activities.count()
            })
        return render(request, "stat/index.html", context=context)



class StatisticView(LoginRequiredMixin, View):
    """图表页视图"""
    def get(self, request):

        return render(request, 'stat/stat.html')
