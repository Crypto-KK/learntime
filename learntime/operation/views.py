import time

import qrcode
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.utils.six import BytesIO
from django.views.generic.base import View

from learntime.activity.models import Activity
from learntime.operation.models import Log, StudentActivity
from learntime.utils.helpers import PaginatorListView, RoleRequiredMixin
from learntime.users.enums import RoleEnum


class LogList(LoginRequiredMixin, PaginatorListView):
    """日志列表页"""
    template_name = "operation/log_list.html"
    context_object_name = "logs"
    paginate_by = 50

    def get_queryset(self):
        if self.request.user.role == 1:
            return Log.objects.all().select_related("user")
        else:
            return Log.objects.filter(user=self.request.user).select_related("user")


class StudentActivityListView(RoleRequiredMixin, PaginatorListView):
    """学生参加活动列表页"""
    role_required = (RoleEnum.ROOT.value, RoleEnum.ACADEMY.value, RoleEnum.STUDENT.value)
    template_name = "operation/student_activity_list.html"
    context_object_name = "objects"
    paginate_by = 50

    def get_queryset(self):
        if self.request.user.role == RoleEnum.ROOT.value: # ROOT级别能看到所有记录
            return StudentActivity.objects.all().select_related("student", "activity")
        elif self.request.user.role == RoleEnum.ACADEMY.value: # 院级能看到所在学院所在年级记录
            return StudentActivity.objects.filter(
                academy=self.request.user.academy,
                grade=self.request.user.grade
            ).select_related("student", "activity")
        elif self.request.user.role == RoleEnum.STUDENT.value:
            # 干部级能够查看参加自己发布活动的学生名单
            my_activity_pks = []
            my_activities = self.request.user.my_activities
            for my_activity in my_activities.all():
                my_activity_pks.append(my_activity.pk)
            return StudentActivity.objects.filter(
                activity_id__in=my_activity_pks).select_related("student", "activity")


class AlterStatusAPIView(View):
    """变更学生参加记录"""
    # role_required = (RoleEnum.ROOT.value, RoleEnum.ACADEMY.value, RoleEnum.STUDENT.value)
    def post(self, request):
        record_pk = request.POST.get("record_pk")
        alter_status = request.POST.get("alter_status")
        try:
            record = StudentActivity.objects.get(pk=record_pk)
            record.status = alter_status
            record.save()
        except Exception:
            return JsonResponse({"status": "fail", "reason": "找不到记录"})
        return JsonResponse({"status": "ok"})


class SignInListView(RoleRequiredMixin, PaginatorListView):
    """签到签退列表页"""
    role_required = (RoleEnum.STUDENT.value,)
    template_name = "operation/sign_in_list.html"
    context_object_name = "activities"
    paginate_by = 20

    def get_queryset(self):
        return Activity.objects.filter(user=self.request.user, is_verify=True)\
            .select_related("user", "to", "to_school")


class QRCodeAPIView(RoleRequiredMixin, View):
    """生成二维码链接"""
    role_required = (RoleEnum.STUDENT.value,)

    def get(self, request, pk, frequency, signInOrSignOut, nonce):
        """
        :param pk: 活动id
        :param frequency: 频率秒
        :param signInOrSignOut: 1为签到，2为签退
        :param nonce: 随机串
        """
        timestamp = int(time.time()) # 秒级时间戳
        return self.generate_qrcode(f"{pk}.{timestamp}.{frequency}.{signInOrSignOut}")

    def generate_qrcode(self, data):
        img = qrcode.make(data)
        buf = BytesIO()
        img.save(buf)
        image_stream = buf.getvalue()
        response = HttpResponse(image_stream, content_type="image/png")
        return response


class PersonListAPIView(RoleRequiredMixin, View):
    """查看报名活动的人员情况"""
    role_required = (RoleEnum.STUDENT.value,)
    def get(self, request, pk):
        """
        :param pk: 活动uuid
        """
        return_data = []
        try:
            activity = Activity.objects.get(pk=pk)
        except Activity.DoesNotExist:
            return JsonResponse({"status": "fail", "reason": "活动不存在"})

        student_activities = activity.join_students.all()
        for obj in student_activities:
            return_data.append({
                "uid": obj.student_id,
                "name": obj.student_name,
                "clazz": obj.clazz,
                "status": obj.get_status_display()
            })

        return JsonResponse({"status": "ok", "count": len(return_data), "data": return_data})
