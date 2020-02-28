from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import DetailView, UpdateView, CreateView, ListView, DeleteView
from django.views.generic.base import View
from django.contrib.sessions.models import Session

from learntime.globalconf.models import Configration, Help
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


class HelpCreateView(RootRequiredMixin, CreateView):
    """帮助文档新建"""
    model = Help
    template_name = "help/create.html"
    fields = "__all__"

    def get_success_url(self):
        messages.success(self.request, "发布帮助文档成功")
        return reverse("conf:help_list")


class HelpListView(ListView):
    """帮助文档列表"""
    model = Help
    template_name = "help/list.html"
    context_object_name = "helps"


class HelpDetailView(DetailView):
    """详情"""
    model = Help
    template_name = "help/detail.html"
    context_object_name = "help"


class HelpUpdateView(RootRequiredMixin, UpdateView):
    model = Help
    template_name = "help/update.html"
    fields = "__all__"

    def get_success_url(self):
        messages.success(self.request, "修改文档成功")
        return reverse("conf:help_list")


class HelpDeleteView(RootRequiredMixin, DeleteView):
    model = Help
    template_name = "help/delete.html"

    def get_success_url(self):
        messages.success(self.request, "删除成功")
        return reverse("conf:help_list")
