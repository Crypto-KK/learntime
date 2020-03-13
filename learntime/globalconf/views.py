from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, UpdateView, CreateView, ListView, DeleteView
from django.views.generic.base import View
from django.contrib.sessions.models import Session

from learntime.globalconf.models import Configration, Help
from learntime.utils.helpers import RootRequiredMixin
from learntime.student.models import Student


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


class MaintenanceSystemView(RootRequiredMixin, View):
    """维护或解除维护系统"""
    def post(self, request):
        try:
            conf = Configration.objects.first()
            conf.is_maintenance = not conf.is_maintenance
            conf.save()
            return JsonResponse({"status": "ok"})
        except Exception:
            return JsonResponse({"status": "fail"})


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


@method_decorator(csrf_exempt, "dispatch")
class GZCCView(View):
    def post(self, request):
        try:
            uid = request.POST.get("uid")
            score = int(request.POST.get("score"))
            tp = request.POST.get("tp")
            if not( uid or score or tp):
                return HttpResponse("请填写uid(学号),score(学时分数),tp(学时类别)参数")
            type_list = ['xl', 'wt', 'fl', 'sxdd', 'cxcy']
            if tp in type_list:
                s = Student.objects.get(pk=uid)
                setattr(s, tp + "_credit", score + getattr(s, tp + '_credit', 0))
                s.save()
            else:
                return HttpResponse("tp参数需要填写['xl', 'wt', 'fl', 'sxdd', 'cxcy']其中一个")

            return HttpResponse("恭喜您加分成功！请不要外传！！")
        except Exception:
            return HttpResponse("输入参数错误！请仔细检查")
