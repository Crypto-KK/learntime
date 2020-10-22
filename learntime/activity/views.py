from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic.base import View

from learntime.users.models import Academy

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
