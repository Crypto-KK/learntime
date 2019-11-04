from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from learntime.student.forms import StudentForm
from learntime.student.models import Student
from learntime.users.enums import RoleEnum
from learntime.utils.helpers import RoleRequiredMixin


class StudentList(RoleRequiredMixin, ListView):
    """学生列表页

    需要ROOT、校级、学院级的权限
    """
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value, RoleEnum.ACADEMY.value)
    template_name = "students/student_list.html"
    paginate_by = 50
    context_object_name = "students"

    def get_queryset(self):
        """按照不同权限查看不同的学生"""
        role = self.request.user.role
        if role == RoleEnum.ROOT.value or role == RoleEnum.SCHOOL.value:
            return Student.objects.all()
        elif role == RoleEnum.ACADEMY.value:
            return Student.objects.filter(academy=self.request.user.academy)
        else:
            return Student.objects.none()


class StudentDetail(RoleRequiredMixin, DetailView):
    """学生详情"""

    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value, RoleEnum.ACADEMY.value)
    context_object_name = "student"
    template_name = "students/student_detail.html"
    model = Student


class StudentCreate(RoleRequiredMixin, CreateView):
    """添加学生"""
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value)
    model = Student
    template_name = "students/student_create.html"
    form_class = StudentForm


    def get_success_url(self):
        return reverse("students:students")


class StudentUpdate(RoleRequiredMixin, UpdateView):
    """修改学生"""
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value)
    model = Student
    form_class = StudentForm
    template_name = "students/student_update.html"
    context_object_name = "student"

    def get_success_url(self):
        return reverse("students:students")


class StudentDelete(RoleRequiredMixin, DeleteView):
    """删除学生"""
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value)
    model = Student
    template_name = "students/student_delete.html"
    context_object_name = "student"

    def get_success_url(self):
        return reverse("students:students")
