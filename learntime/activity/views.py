from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import ListView, CreateView, DetailView

from learntime.activity.forms import ActivityForm
from learntime.activity.models import Activity
from learntime.users.enums import RoleEnum
from learntime.utils.helpers import RoleRequiredMixin


class ActivityList(RoleRequiredMixin, ListView):
    """活动列表页

    需要ROOT、校级、学院级的权限
    """
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value,
                     RoleEnum.ACADEMY.value, RoleEnum.STUDENT.value)
    template_name = "activity/activity_list.html"
    paginate_by = 20
    context_object_name = "activities"


    def get_queryset(self):
        """按照不同权限查看不同的学生"""
        role = self.request.user.role
        if role == RoleEnum.ROOT.value or role == RoleEnum.SCHOOL.value:
            return Activity.objects.all().order_by("-time") #按照活动时间排序
        elif role == RoleEnum.ACADEMY.value:
            pass
        elif role == RoleEnum.STUDENT.value:
            return Activity.objects.none()


class ActivityCreate(RoleRequiredMixin, CreateView):
    """添加活动"""
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value,
                     RoleEnum.ACADEMY.value, RoleEnum.STUDENT.value)
    model = Activity
    template_name = "activity/activity_create.html"
    form_class = ActivityForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("activities:activities")


class ActivityDetail(LoginRequiredMixin, DetailView):
    """活动详情"""
    model = Activity
    template_name = "activity/activity_detail.html"
    context_object_name = "activity"
