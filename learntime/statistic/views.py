import json

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic.base import View
from pyecharts.charts import Bar, Line
from pyecharts.globals import ThemeType

from learntime.globalconf.models import Configration
from learntime.activity.models import Activity
from learntime.student.models import Student
from learntime.users.enums import RoleEnum
from learntime.utils.echarts_utils import EchartsResponse
from pyecharts import options as opts

from learntime.statistic.models import CreditStat

User = get_user_model()

def rank_chart_view(request, maximum):
    """学时排名统计"""
    title = "学时排名"
    students = Student.objects.all()
    if request.user.role == RoleEnum.ACADEMY.value:
        students = students.filter(grade=request.user.grade, academy=request.user.academy)
        title = f'{request.user.academy}{request.user.grade}学时排名'
    if maximum > 20:
        maximum = 20
    students = students[:maximum]

    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            .add_xaxis([student.name for student in students])
            .add_yaxis("总学时", [student.credit for student in students])
            .set_global_opts(title_opts=opts.TitleOpts(title=title))
            .set_colors(['#60acfc', '#5bc49f', '#ff7c7c'])
            .dump_options_with_quotes()
    )
    return EchartsResponse(json.loads(c))



def class_average_credit_view(request):
    """班级平均学时柱状图"""
    students = Student.objects.all()

    if request.user.role == RoleEnum.ACADEMY.value:
        students = students.filter(grade=request.user.grade, academy=request.user.academy)
        avgs = {}
        averages = {}
        for student in students:
            key = student.clazz
            try:
                avgs[key]
            except Exception:
                avgs[key] = []
            avgs[key].append(student.credit)

        for clazz, credits in avgs.items():
            averages[clazz] = round(sum(credits) / len(credits), 2)
        del avgs

        print(averages)

    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
            .add_xaxis([k for k in averages.keys()])
            .add_yaxis("班级平均学时", [v for v in averages.values()])
            .set_global_opts(title_opts=opts.TitleOpts(title="班级平均学时图"))
            .set_colors(['#60acfc', '#5bc49f', '#ff7c7c'])
            .dump_options_with_quotes()
    )

    return EchartsResponse(json.loads(c))



def grade_average_credit_change_per_month_view(request):
    """年级每月的平均学时变化趋势折线图"""
    objs = CreditStat.objects.all() # 获取所有对象

    record_time_distinct = objs.values("record_time").distinct() # 获取所有的日期（不重复）

    record_time_list = [record_time_distinct[i]['record_time']
                        for i in range(len(record_time_distinct))] # 将所有日期打包成列表

    diff_dict = {} # 变化字典
    for record_time in record_time_list:
        diff_dict[record_time.strftime("%Y年%m月")] = {} # 给字典赋初始值，key为所有的日期


    if request.user.role == RoleEnum.ACADEMY.value: # 辅导员级别
        objs = objs.filter(academy=request.user.academy)

        for month in record_time_list:
            this_month_objs = objs.filter(record_time=month)
            for this_month_obj in this_month_objs:
                try:
                    diff_dict[this_month_obj.record_time.strftime("%Y年%m月")][this_month_obj.grade]
                except Exception:
                    diff_dict[this_month_obj.record_time.strftime("%Y年%m月")][this_month_obj.grade] = []
                diff_dict[this_month_obj.record_time.strftime("%Y年%m月")][this_month_obj.grade].append(
                    this_month_obj.diff
                )

        print(diff_dict)
        for k1, v1 in diff_dict.items():
            for k2, v2 in v1.items():
                diff_dict[k1][k2] = sum(v2) / len(v2)

        print(diff_dict)
        # diff_dict 格式如下
        # {
        #     "2020年3月": {
        #         "2017级": 2,
        #         "2018级": 3
        #     },
        #     "2020年4月": {
        #         "2017级": 0,
        #         "2018级": 1
        #     },
        # }


        c = (
            Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
                .add_xaxis([v.strftime("%Y年%m月") for v in record_time_list])
                .add_yaxis("年级趋势图", [3,4,5])
                .set_global_opts(title_opts=opts.TitleOpts(title="班级平均学时图"))
                .set_colors(['#60acfc', '#5bc49f', '#ff7c7c'])
                .dump_options_with_quotes()
        )

        return EchartsResponse(json.loads(c))



class IndexView(LoginRequiredMixin, View):
    """首页视图"""
    def get(self, request):
        context = {
            "activity_nums": Activity.objects.count(),
            "notice": Configration.objects.first().notice
        }
        role = request.user.role
        if role == RoleEnum.ROOT.value:
            # root能看到管理员数量和等待审核的管理员数量
            context.update({
                "student_nums": Student.objects.all().count(),
                "admin_nums": User.objects.filter(is_active=True).count(),
                "verifying_admin_nums": User.objects.filter(is_active=False).count()
            })
        elif role == RoleEnum.SCHOOL.value:
            # 学校级管理员能看到等待自己审核的活动数量
            context.update({
                "student_nums": Student.objects.count(),
                "verifying_activities_nums": request.user.school_waiting_for_verify_activities.count()
            })

        elif role == RoleEnum.ACADEMY.value:
            # 学院管理员能看到等待自己审核的活动数量
            context.update({
                "student_nums": Student.objects.filter(grade=request.user.grade,
                                                       academy=request.user.academy).count(),
                "verifying_activities_nums": request.user.waiting_for_verify_activities.count()
            })

        elif role == RoleEnum.ORG.value:
            # 学生组织账号能够看到全学院所有学生
            context.update({
                "student_nums": Student.objects.filter(academy=request.user.academy).count(),
                "verifying_activities_nums": request.user.waiting_for_verify_activities.count()
            })
        return render(request, "stat/index.html", context=context)



class StatisticView(LoginRequiredMixin, View):
    """图表页视图"""
    def get(self, request):

        return render(request, 'stat/stat.html')
