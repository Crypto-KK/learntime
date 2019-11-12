from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.views.generic.base import View

from rest_framework import mixins, viewsets

from learntime.activity.forms import ActivityForm
from learntime.activity.models import Activity
from learntime.activity.serializers import ActivitySerializer
from learntime.users.enums import RoleEnum
from learntime.users.models import Academy
from learntime.utils.helpers import RoleRequiredMixin, PaginatorListView


class ActivityList(RoleRequiredMixin, PaginatorListView):
    """我发布的活动列表 干部级可以在这里发布活动，查看自己的活动

    需要ROOT、校级、学院级的权限
    """
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value,
                     RoleEnum.ACADEMY.value, RoleEnum.STUDENT.value)
    template_name = "activity/activity_list.html"
    paginate_by = 20
    context_object_name = "activities"

    def get_queryset(self):
        """返回我发布的活动"""
        return Activity.objects.filter(user=self.request.user)


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
    """添加活动"""
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value,
                     RoleEnum.ACADEMY.value, RoleEnum.STUDENT.value)
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
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("activities:activities")


class ActivityDetail(LoginRequiredMixin, DetailView):
    """活动详情"""
    model = Activity
    template_name = "activity/activity_detail.html"
    context_object_name = "activity"


class ActivityUpdate(RoleRequiredMixin, UpdateView):
    """修改活动"""
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value)
    model = Activity
    form_class = ActivityForm
    template_name = "activity/activity_update.html"
    context_object_name = "activity"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("activities:activities")


@method_decorator(csrf_exempt, "dispatch")
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
        except Exception:
            return JsonResponse({"status": "fail"})
        else:
            return JsonResponse({"status": "ok"})


@method_decorator(csrf_exempt, "dispatch")
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


@method_decorator(csrf_exempt, "dispatch")
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


@method_decorator(csrf_exempt, "dispatch")
class GetAdminsView(LoginRequiredMixin, View):
    """通过学院id获取该学院的所有管理员"""
    def post(self, request):
        try:
            admin_dict = {}
            academy = Academy.objects.get(pk=request.POST['id'])
            admins = get_user_model().objects.filter(academy__contains=academy)
            for admin in admins:
                admin_dict.update({admin.pk: admin.name})

            return JsonResponse({
                "status": "ok",
                "admin_dict": admin_dict
            })
        except Exception:
            return JsonResponse({"status": "fail"})


class StoreDetailViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):

    serializer_class = ActivitySerializer

    def get_queryset(self):
        return Activity.objects.all()
