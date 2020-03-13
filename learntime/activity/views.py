from datetime import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from django.views.generic.base import View

from learntime.activity.tasks import send_activity_verify_email
from learntime.activity.forms import ActivityForm, ActivityCraftForm
from learntime.activity.models import Activity
from learntime.users.enums import RoleEnum
from learntime.users.models import Academy
from learntime.utils.helpers import RoleRequiredMixin, PaginatorListView, AuthorRequiredMixin


class AllActivityList(RoleRequiredMixin, PaginatorListView):
    """管理员权限：看到所有活动"""
    role_required = (RoleEnum.ROOT.value, )
    template_name = "activity/all_activity_list.html"
    paginate_by = 20
    context_object_name = "activities"

    def get_queryset(self):
        """返回全部"""
        return Activity.objects.filter(is_craft=False).select_related('user', 'to', 'to_school')


class MyActivityList(RoleRequiredMixin, PaginatorListView):
    """我发布的活动列表 干部级可以在这里发布活动，查看自己的活动
    只能由干部操作
    """
    role_required = (RoleEnum.STUDENT.value,)
    template_name = "activity/activity_list.html"
    paginate_by = 10
    context_object_name = "activities"

    def get_queryset(self):
        """返回我发布的活动"""
        now = datetime.now()
        activities = Activity.objects.filter(user=self.request.user, is_craft=False)
        # 获取所有已经超过截止时间的活动
        activities_update_list = activities.filter(stop=False, is_verify=True, deadline__lt=now)
        if activities_update_list.__len__() > 0:
            activities_update_list.update(stop=True)
        return activities


class MyActivityCraftList(RoleRequiredMixin, PaginatorListView):
    """我的草稿箱"""
    role_required = (RoleEnum.STUDENT.value,)
    template_name = "activity/activity_craft_list.html"
    paginate_by = 10
    context_object_name = "activities"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['academies'] = Academy.objects.all()
        return context
    def get_queryset(self):
        """返回我的草稿箱内容"""
        return Activity.objects.filter(user=self.request.user, is_craft=True)


class ActivityUnVerifyList(RoleRequiredMixin, PaginatorListView):
    """活动等待审核列表页

    需要ROOT、校级、学院级的权限
    """
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value,
                     RoleEnum.ACADEMY.value)
    template_name = "activity/activity_unverify_list.html"
    paginate_by = 20
    context_object_name = "activities"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context['admins'] = get_user_model().objects.filter(role=RoleEnum.SCHOOL.value)
        return context

    def get_queryset(self):
        """按照不同权限查看不同的活动"""
        role = self.request.user.role
        if role == RoleEnum.ROOT.value:
            # 返回全部正在审核的活动
            return Activity.objects.filter(is_verifying=True)
        if role == RoleEnum.SCHOOL.value:
            # 返回需要自己审核的活动
            return self.request.user.school_waiting_for_verify_activities.filter(is_verifying=True)
        if role == RoleEnum.ACADEMY.value:
            return self.request.user.waiting_for_verify_activities.filter(is_verifying=True)
        else:
            # 返回空
            return Activity.objects.none()


class ActivityVerifyList(ActivityUnVerifyList):
    """活动审核通过的页面"""
    template_name = "activity/activity_verify_list.html"
    def get_queryset(self):
        role = self.request.user.role
        if role == RoleEnum.ROOT.value:
            return Activity.objects.filter(is_verify=True).order_by("-time") #按照活动时间排序
        if role == RoleEnum.SCHOOL.value:
            # 返回to_school为自己的活动
            return self.request.user.school_waiting_for_verify_activities.filter(is_verify=True)
        elif role == RoleEnum.ACADEMY.value:
            # 返回自己审核通过的活动
            return self.request.user.waiting_for_verify_activities.filter(is_verify=True)
        else:
            # 返回空
            return Activity.objects.none()


class ActivityCreate(RoleRequiredMixin, CreateView):
    """发布活动，只能由干部发布"""
    role_required = (RoleEnum.STUDENT.value, )
    model = Activity
    template_name = "activity/activity_create.html"
    form_class = ActivityForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['academies'] = Academy.objects.all()
        return context

    def form_valid(self, form):
        # 指定审核者
        to_admin = get_user_model().objects.get(pk=self.request.POST['to'])
        form.instance.to = to_admin
        form.instance.user = self.request.user
        form.instance.is_craft = False #
        # 发送异步邮件给指定的审核者 to_admin
        send_activity_verify_email(to_admin.email)
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "发布活动成功")
        return reverse("activities:activities")


class ActivityCraftCreate(RoleRequiredMixin, CreateView):
    """保存到草稿中"""
    role_required = (RoleEnum.STUDENT.value, )
    model = Activity
    template_name = "activity/activity_create.html"
    form_class = ActivityCraftForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['academies'] = Academy.objects.all()
        return context

    def form_valid(self, form):
        # 指定审核者
        form.instance.user = self.request.user
        form.instance.is_craft = True
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "保存到草稿箱成功！")
        return reverse("activities:craft_list")


class ActivityCraftUpdate(AuthorRequiredMixin, UpdateView):
    """继续编辑草稿箱的内容"""
    model = Activity
    form_class = ActivityCraftForm
    template_name = "activity/activity_craft_update.html"
    context_object_name = "activity"

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.is_craft = True
        print(form.instance.logo)
        print(form.instance.file)
        return super().form_valid(form)

    def get_success_url(self):
        if self.request.GET.get("continue"):
            return reverse("activities:craft_update", kwargs={"pk": self.kwargs['pk']})
        else:
            messages.success(self.request, "修改草稿箱成功")
            return reverse("activities:craft_list")



class ActivityCraftPublish(AuthorRequiredMixin, View):
    """草稿箱内容直接发ActivityForm布"""
    def post(self, request):
        activity_id = request.POST.get("activity_id")
        admin_id = request.POST.get("admin_id")
        if activity_id and admin_id:
            try:
                activity = Activity.objects.get(pk=activity_id)
                admin = get_user_model().objects.get(pk=admin_id)
            except Exception:
                return JsonResponse({"status": "unknown", "err": "审核人查找失败"})
            if activity.is_craft:
                # 草稿才能发布
                activity.user = request.user
                activity.to = admin
                activity.is_craft = False
                form = ActivityForm(data=activity.__dict__, instance=activity)
                if form.is_valid():
                    activity.save()
                    return JsonResponse({"status": "ok"})
                else:
                    return JsonResponse({"status": "fail", "err": form.errors})
            else:
                return JsonResponse({"status": "unknown", "err": "草稿才能发布"})



class ActivityDetail(LoginRequiredMixin, DetailView):
    """活动详情"""
    model = Activity
    template_name = "activity/activity_detail.html"
    context_object_name = "activity"


class ActivityUpdate(AuthorRequiredMixin, UpdateView):
    """修改活动"""
    model = Activity
    form_class = ActivityForm
    template_name = "activity/activity_update.html"
    context_object_name = "activity"

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.is_craft = False
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "修改活动成功")
        return reverse("activities:activities")


class ActivityDelete(AuthorRequiredMixin, View):
    """删除活动接口"""
    def post(self, request):
        try:
            activity_id = request.POST.get('activity_id')
            Activity.objects.get(pk=activity_id).delete()
            # 记录日志
        except Exception:
            return JsonResponse({'status': 'fail'})
        messages.success(self.request, "删除活动成功")
        return JsonResponse({'status': 'ok'})


class ActivityVerifyView(RoleRequiredMixin, View):
    """批准审核接口"""
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value, RoleEnum.ACADEMY.value)

    def post(self, request):
        """
        点击审核通过按钮 is_verify = True, is_verifying = False
        """
        uid = request.POST['uid']
        try:
            activity = Activity.objects.get(pk=uid)
            activity.is_verify = True
            activity.is_verifying = False
            activity.save()
            # 此处写入到activity表
        except Exception as e:
            print(e)
            return JsonResponse({"status": "fail"})
        else:
            return JsonResponse({"status": "ok"})


class ActivityVerifyFailView(RoleRequiredMixin, View):
    """不批准审核接口"""
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value, RoleEnum.ACADEMY.value)

    def post(self, request):
        """
        正在审核置为False，是否审核置为False
        """
        uid = request.POST['uid']
        reason = request.POST['reason']
        try:
            activity = Activity.objects.get(pk=uid)
            activity.is_verify = False
            activity.is_verifying = False
            activity.reason = reason
            activity.save()
        except Exception as e:
            return JsonResponse({"status": "fail"})
        else:
            return JsonResponse({"status": "ok"})


class ActivityPassVerifyView(RoleRequiredMixin, View):
    """传递给上级审核接口"""
    role_required = (RoleEnum.ACADEMY.value,)

    def post(self, request):
        """
        院级传递给校级，to_school指向校级管理员，to指向自己
        """
        activity_id = request.POST['activity_id']
        admin_id = request.POST['admin_id']
        try:
            activity = Activity.objects.get(pk=activity_id)
            admin = get_user_model().objects.get(pk=admin_id)
            activity.to_school = admin
            activity.save()
        except Exception:
            return JsonResponse({"status": "fail"})
        else:
            return JsonResponse({"status": "ok"})


class GetAdminsView(LoginRequiredMixin, View):
    """通过学院id获取该学院的所有管理员"""
    def post(self, request):
        try:
            admin_dict = {}
            academy = Academy.objects.get(pk=request.POST['id'])
            admins = get_user_model().objects.filter(academy__contains=academy, role=3)
            for admin in admins:
                admin_dict.update({admin.pk: f'{admin.name}({admin.grade})'})

            return JsonResponse({
                "status": "ok",
                "admin_dict": admin_dict
            })
        except Exception:
            return JsonResponse({"status": "fail"})
