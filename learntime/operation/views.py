import time

import qrcode
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.utils.six import BytesIO
from django.views.generic import ListView, CreateView, DeleteView
from django.views.generic.base import View

from learntime.activity.models import Activity
from learntime.operation.models import Log, StudentActivity, Comment, FeedBack
from learntime.utils.helpers import PaginatorListView, RoleRequiredMixin, RootRequiredMixin
from learntime.users.enums import RoleEnum
from learntime.operation.tasks import send_email_to_user


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


class CommentList(LoginRequiredMixin, PaginatorListView):
    template_name = "operation/comment_list.html"
    context_object_name = "comments"
    paginate_by = 50
    model = Comment



class StudentActivityListView(LoginRequiredMixin, PaginatorListView):
    """学生参加活动列表页"""
    template_name = "operation/student_activity_list.html"
    context_object_name = "objects"
    paginate_by = 50

    def get_queryset(self):
        if self.request.user.role == RoleEnum.ROOT.value or self.request.user.role == RoleEnum.SCHOOL.value: # ROOT级别能看到所有记录
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


class SearchRecordByPkAndTypeAPIView(LoginRequiredMixin, View):
    """查找某个学生某个类型的参加活动记录"""
    def get(self, request):
        """
        :param request:
        :param student_id: 学号
        :param type_name: 参与的类型
        :return:
        """
        student_id = request.GET.get("student_id")
        type_name = request.GET.get("type_name")
        if not student_id:
            return JsonResponse({"status": "fail", "reason": "学号查找不到"})

        if not type_name:
            records = StudentActivity.objects.filter(student__uid=student_id)
        else:
            records = StudentActivity.objects.filter(student__uid=student_id,
                                       credit_type=type_name)
            print(records)
        results = []
        for record in records:
            results.append({
                "activity_name": record.activity_name,
                "credit": record.credit,
                "credit_type": record.credit_type,
                "student_name": record.student_name,
                "create_time": record.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": record.get_status_display()
            })

        return JsonResponse({"status": "ok", "data": results})


class FeedBackListView(LoginRequiredMixin, PaginatorListView):
    """反馈列表"""
    paginate_by = 20
    context_object_name = "feedbacks"
    template_name = "operation/feedback_list.html"

    def get_queryset(self):
        if self.request.user.role == RoleEnum.ROOT.value:
            # 管理员
            return FeedBack.objects.all()
        else:
            return FeedBack.objects.filter(email=self.request.user.email)


class FeedBackCreateView(RoleRequiredMixin, CreateView):
    role_required = (RoleEnum.SCHOOL.value, RoleEnum.ACADEMY.value, RoleEnum.STUDENT.value)
    template_name = "operation/feedback_create.html"
    fields = ('content', )
    model = FeedBack

    def form_valid(self, form):
        form.instance.name = self.request.user.name
        form.instance.email = self.request.user.email
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "提交反馈成功！")
        return reverse("operations:feedback_list")


class FeedBackDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "operation/feedback_delete.html"
    model = FeedBack
    context_object_name = "feedback"
    def get_success_url(self):
        messages.success(self.request, "删除反馈成功！")
        return reverse("operations:feedback_list")


class FeedBackDetailAPIView(LoginRequiredMixin, View):
    """反馈详情api接口"""
    def get(self, request):
        try:
            feedback_id = request.GET.get('feedback_id')
            feedback = FeedBack.objects.get(pk=feedback_id)
            return JsonResponse({
                "status": "ok",
                "content": feedback.content,
                "name": feedback.name
            })
        except Exception:
            return JsonResponse({"status": "fail"})


class SendEmailAPIView(RootRequiredMixin, View):
    """发送邮件接口"""
    def post(self, request):
        try:
            title = request.POST.get("title")
            content = request.POST.get("content")
            email = request.POST.get("email")
            feedback_id = request.POST.get("feedback_id")

            # 修改数据库记录
            feedback = FeedBack.objects.get(pk=feedback_id)
            feedback.is_fix = True
            feedback.reply = content
            feedback.save()
            send_email_to_user(email, title, content)

        except Exception:
            return JsonResponse({"status": "fail"})
        return JsonResponse({"status": "ok"})
