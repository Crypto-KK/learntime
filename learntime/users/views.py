from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from django.views.generic.base import View

from learntime.activity.models import Activity
from learntime.student.models import Student
from learntime.users.enums import RoleEnum
from learntime.users.forms import LoginForm, RegisterForm, UserForm, AcademyForm, GradeForm
from learntime.users.models import Academy, Grade
from learntime.utils.helpers import AuthorRequiredMixin, RoleRequiredMixin, PaginatorListView

User = get_user_model() # 惰性获取User对象


class IndexView(LoginRequiredMixin, View):
    """首页视图"""
    def get(self, request):
        context = {
            "student_nums": Student.objects.count(),
            "activity_nums": Activity.objects.count(),
            "admin_nums": User.objects.filter(is_active=True).count(),
            "verifying_admin_nums": User.objects.filter(is_active=False).count(),
            "activities": Activity.objects.all().order_by("-updated_at"),

        }
        if request.user.role == RoleEnum.ROOT.value or request.user.role == RoleEnum.SCHOOL.value:
            return render(request, "front/index.html", context=context)
        else:
            return render(request, "front/index.html")

def login_view(request):
    """登录视图

    使用邮箱做为登录账号
    """
    next = request.GET.get('next', '')
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'users/login.html', {'form': form})
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                if next == "":
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return HttpResponseRedirect(next)
        return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """注销视图，重定向到登录界面"""
    logout(request)
    return redirect(reverse_lazy("users:login"))


def register_view(request):
    """注册为管理员

    注册后需要等待后台审核，审核成功后is_active置为True
    """
    if request.method == "GET":
        form = RegisterForm()
        return render(request, 'users/register.html', {'form': form,
                                                       "academies": Academy.objects.all(),
                                                       "grades": Grade.objects.all()})
    elif request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():

            user = User(
                username=form.cleaned_data['username'],
                email = form.cleaned_data['email'],
                name = form.cleaned_data['name'],
                identity = form.cleaned_data['identity'],
            )
            if form.cleaned_data['identity'] != 2:
                user.academy = form.cleaned_data['academy']
                user.grade = form.cleaned_data['grade']

            user.set_password(form.cleaned_data['password'])
            user.register()
            return render(request, 'users/register_success.html')

        return render(request, 'users/register.html', {'form': form})


class AdminApplyList(RoleRequiredMixin, PaginatorListView):
    """等待审核的用户列表

    需要ROOT、校级的权限
    """
    template_name = "users/admin_apply.html"
    context_object_name = "admins"
    paginate_by = 20
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value)

    def get_queryset(self):
        """获取正在审核的用户"""
        return User.objects.filter(is_active=False)


class AdminList(RoleRequiredMixin, ListView):
    """管理员列表页

    需要ROOT、校级、学院级的权限
    """
    template_name = "users/admin_list.html"
    context_object_name = "admins"
    paginate_by = 20
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value, RoleEnum.ACADEMY.value)

    def get_queryset(self):
        """按照不同权限查看不同的管理员"""
        role = self.request.user.role
        if role == RoleEnum.ROOT.value or role == RoleEnum.SCHOOL.value:
            return User.objects.filter(is_active=True)
        elif role == RoleEnum.ACADEMY.value:
            return User.objects.filter(
                role=RoleEnum.ACADEMY.value, is_active=True)
        else:
            return User.objects.none()


class AdminDetail(RoleRequiredMixin, DetailView):
    """管理员详情页

    需要ROOT、校级的权限
    """
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value)
    context_object_name = 'admin'
    template_name = "users/admin_detail.html"
    model = User


class AdminUpdateView(RoleRequiredMixin, UpdateView):
    """修改资料"""
    role_required = (RoleEnum.ROOT.value, )
    model = User
    context_object_name = "user"
    template_name = "users/change_profile.html"
    form_class = UserForm

    def get_success_url(self):
        messages.success(self.request, "修改资料成功")
        return reverse_lazy("users:admins")


class AdminDeleteView(RoleRequiredMixin, DeleteView):
    """删除管理员

    此操作需要ROOT或校级的权限
    """
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value, )
    model = User
    template_name = "users/admin_delete.html"
    context_object_name = "admin"

    def get_success_url(self):
        messages.warning(self.request, "删除管理员成功")
        return reverse_lazy("users:admins")


@method_decorator(csrf_exempt, name="dispatch")
class ApplyConfirmView(RoleRequiredMixin, View):
    """批准用户注册为管理员

    需要ROOT、校级、的权限
    """
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value, )

    def post(self, request):
        try:
            data = request.body.decode("utf-8").split("&")
            role_id = data[0].split("=")[1]
            username = data[1].split("=")[1]
            user = User.objects.get(username=username)
            user.role = role_id  # 增加用户权限
            user.is_active = True  # 激活用户
            user.save()

        except Exception as e:
            print(e)
            return JsonResponse({"err": 1})

        else:
            return JsonResponse({"err": 0})

# =============================================================================
# =================================年级和学院视图=================================

class AcademyList(RoleRequiredMixin, ListView):
    """学院列表页"""
    role_required = (RoleEnum.ROOT.value, )
    template_name = "academy/list.html"
    context_object_name = "academies"
    model = Academy


class AcademyCreate(RoleRequiredMixin, CreateView):
    """新增学院"""
    role_required = (RoleEnum.ROOT.value,)
    model = Academy
    form_class = AcademyForm
    template_name = "academy/create.html"

    def get_success_url(self):
        messages.success(self.request, "添加学院成功")
        return reverse_lazy("academy")


class AcademyUpdate(RoleRequiredMixin, UpdateView):
    """修改学院"""
    role_required = (RoleEnum.ROOT.value,)
    model = Academy
    form_class = AcademyForm
    template_name = "academy/update.html"

    def get_success_url(self):
        messages.warning(self.request, "修改学院成功")
        return reverse_lazy("academy")


class AcademyDelete(RoleRequiredMixin, DeleteView):
    """删除学院"""
    role_required = (RoleEnum.ROOT.value,)
    model = Academy
    template_name = "academy/delete.html"

    def get_success_url(self):
        messages.warning(self.request, "删除学院成功")
        return reverse_lazy("academy")


class GradeList(RoleRequiredMixin, ListView):
    """学院列表页"""
    role_required = (RoleEnum.ROOT.value, )
    template_name = "grade/list.html"
    context_object_name = "grades"
    model = Grade

# GradeList = type('GradeList', (RoleRequiredMixin, ListView, object,), {
#     'role_required': (RoleEnum.ROOT.value, ),
#     'template_name': "grade/list.html",
#     'context_object_name': "grades",
#     "model": Grade
# })

class GradeCreate(RoleRequiredMixin, CreateView):
    """新增年级"""
    role_required = (RoleEnum.ROOT.value,)
    model = Grade
    form_class = GradeForm
    template_name = "grade/create.html"

    def get_success_url(self):
        messages.success(self.request, "新增年级成功")
        return reverse_lazy("grade")


class GradeDelete(RoleRequiredMixin, DeleteView):
    """删除年级"""
    role_required = (RoleEnum.ROOT.value,)
    model = Grade
    template_name = "grade/delete.html"

    def get_success_url(self):
        messages.warning(self.request, "删除年级成功")
        return reverse_lazy("grade")
