from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import DetailView, UpdateView
from django.views.generic.base import View
from django.contrib.sessions.models import Session

from learntime.globalconf.models import Configration
from learntime.utils.helpers import RootRequiredMixin


class ConfDetailView(RootRequiredMixin, DetailView):
    """配置查看页面"""
    template_name = "conf/detail.html"
    context_object_name = "conf"

    def get_object(self, queryset=None):
        return Configration.objects.first()


class ConfEditView(RootRequiredMixin, UpdateView):
    """配置编辑页面"""
    template_name = "conf/edit.html"
    context_object_name = "conf"
    model = Configration
    fields = ['notice', "maintenance_notice", "criterion", "default_password",
              "is_maintenance", "database_host", "database_user", "database_pass"]

    def get_success_url(self):
        messages.success(self.request, "编辑配置成功")
        return reverse("conf:show")


class RemoveSessionView(RootRequiredMixin, View):
    """清空所有session"""
    def post(self, request):
        try:
            Session.objects.all().delete()
        except Exception:
            return JsonResponse({"status": "fail"})

        return JsonResponse({"status": "ok"})
