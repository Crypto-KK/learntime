import json

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.base import View
from pyecharts.charts import Bar
from pyecharts.globals import ThemeType

from learntime.activity.models import Activity
from learntime.student.models import Student
from learntime.users.enums import RoleEnum
from learntime.utils.echarts_utils import EchartsResponse
from pyecharts import options as opts


User = get_user_model()

def chart_view(request):
    students = Student.objects.all()[:10]

    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            .add_xaxis([student.name for student in students])
            .add_yaxis("总学时", [student.credit for student in students])
            .set_global_opts(title_opts=opts.TitleOpts(title="TOP 10"))
            .dump_options_with_quotes()
    )
    return EchartsResponse(json.loads(c))


class IndexView(LoginRequiredMixin, View):
    """首页视图"""
    def get(self, request):
        context = {
            "student_nums": Student.objects.count(),
            "activity_nums": Activity.objects.count(),
            "admin_nums": User.objects.filter(is_active=True).count(),
            "verifying_admin_nums": User.objects.filter(is_active=False).count(),
        }
        if request.user.role == RoleEnum.ROOT.value or request.user.role == RoleEnum.SCHOOL.value:
            return render(request, "stat/index.html", context=context)
        else:
            return render(request, "stat/index.html")
