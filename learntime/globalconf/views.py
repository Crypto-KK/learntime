from django.contrib import messages
from django.urls import reverse
from django.views.generic import DetailView, UpdateView

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
    fields = ['notice', "is_maintenance", "criterion"]

    def get_success_url(self):
        messages.success(self.request, "编辑配置成功")
        return reverse("conf:show")
