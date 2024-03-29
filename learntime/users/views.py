from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, \
    PasswordResetDoneView, PasswordChangeView, PasswordChangeDoneView, \
    PasswordResetCompleteView
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import UpdateView, DeleteView, CreateView, DetailView
from django.views.generic.base import View
import random
from django.core.cache import cache

from learntime.globalconf.models import Configration
from learntime.users.enums import RoleEnum
from learntime.users.forms import LoginForm, RegisterForm, UserForm, ForgetForm, InstituteForm
from learntime.users.models import Academy, Grade, Institute
from learntime.utils.factories import CrudViewFactory
from learntime.utils.helpers import PaginatorListView, RootRequiredMixin, FormInitialMixin, RoleRequiredMixin
from learntime.operation.models import Log
from learntime.users.tasks import send_user_verify_email, send_code_email

User = get_user_model() # 惰性获取User对象


@method_decorator(sensitive_post_parameters('password'), 'dispatch')
class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'users/registration/login.html', {'form': form})

    def post(self, request):
        # print(request.POST)
        # form = LoginForm(request.POST)
        email = request.POST.get("email")
        password = request.POST.get("password")
        next = request.GET.get('next', '')
        if not (email is None or password is None):
            print(email, password)
            user = authenticate(username=email, password=password)
            if user is not None:
                if user.is_freeze:
                    return render(request, 'users/registration/login.html', {'error': "该账号已被冻结，请联系管理员"})
                else:
                    login(request, user)
                    if next == "":
                        return HttpResponseRedirect(reverse('index'))
                    else:
                        return HttpResponseRedirect(next)

        return render(request, 'users/registration/login.html', {'error': "账号名或密码错误"})


def logout_view(request):
    """注销视图，重定向到登录界面"""
    logout(request)
    return redirect(reverse("users:login"))


@method_decorator(sensitive_post_parameters('password', 'password2'), 'dispatch')
class RegisterView(View):
    """注册为管理员
    注册后需要等待后台审核，审核成功后is_active置为True
    """
    context = {
        'form': RegisterForm(),
         "academies": Academy.objects.all(),
         "grades": Grade.objects.all(),
         'organizations': Institute.objects.all()
    }
    def get(self, request):
        return render(request, 'users/registration/register.html', self.context)
    def post(self, request):
        form = RegisterForm(request.POST)
        print(form.errors)
        if form.is_valid():
            user = User(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                name=form.cleaned_data['name'],
                role=form.cleaned_data['role'],
            )
            if form.cleaned_data['role'] != 2:
                user.academy = form.cleaned_data['academy']
                user.grade = form.cleaned_data['grade']
                if form.cleaned_data['role'] == 4:
                    # 学时干部
                    user.organization = form.cleaned_data['organization']
            else:
                # 校级用户
                user.department = form.cleaned_data['department']

            user.set_password(form.cleaned_data['password'])
            user.register()
            return render(request, 'users/registration/register_success.html')

        return render(request, 'users/registration/register.html', self.context)


class EmailChangeView(View, LoginRequiredMixin):
    """更改邮箱
    需要发送验证码到当前绑定的邮箱，验证通过后才能修改邮箱
    """
    def get(self, request):
        # 发送邮箱校验码
        code = str(random.randrange(1000, 9999))
        email = request.user.email
        # 300秒过期时间
        cache.set("change-" + email, code, 300)
        send_code_email(email, code)
        return JsonResponse({})

    def post(self, request):
        # 更改邮箱
        old_email = request.user.email
        real_code = cache.get('change-' + old_email)
        code = request.POST.get('code')
        new_email = request.POST.get('email')

        if code == real_code:
            # 验证通过
            request.user.email = new_email
            request.user.save()
            return JsonResponse({
                'status': 'ok'
            })
        else:
            return JsonResponse({
                'status': 'fail'
            })

class MyPasswordResetView(PasswordResetView):
    """重置密码视图"""
    template_name = 'users/registration/forget_pwd.html'
    form_class = ForgetForm
    success_url = reverse_lazy("users:password_reset_done")
    email_template_name = 'users/registration/password_reset_email.html'


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    """重置密码页面，输入两次密码"""
    template_name = 'users/registration/password_change_form.html'
    success_url = reverse_lazy('users:password_reset_complete')


class MyPasswordResetDoneView(PasswordResetDoneView):
    """发送确认重置邮件"""
    template_name = 'users/registration/password_reset_done.html'


class MyPasswordResetCompleteView(PasswordResetCompleteView):
    """完成重置密码"""
    template_name = 'users/registration/password_change_done.html'



class MyPasswordChangeView(PasswordChangeView):
    """更改密码页面"""
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/registration/password_change_form.html'


class MyPasswordChangeDoneView(PasswordChangeDoneView):
    """更改密码完成"""
    template_name = 'users/registration/password_change_done.html'


class AdminApplyList(RootRequiredMixin, PaginatorListView):
    """等待审核的用户列表 需要ROOT的权限"""
    template_name = "users/admin_apply_list.html"
    context_object_name = "admins"
    paginate_by = 20

    def get_queryset(self):
        """获取正在审核的用户"""
        return User.objects.filter(is_active=False)


class AdminList(RootRequiredMixin, PaginatorListView):
    """管理员列表页需要ROOT"""
    template_name = "users/admin_list.html"
    context_object_name = "admins"
    paginate_by = 100

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        academies = Academy.objects.values_list("name")
        context['academy_list'] = [name[0] for name in academies]
        return context

    def get_queryset(self):
        """按照不同权限查看不同的管理员"""
        academy = self.request.GET.get('academy')
        name = self.request.GET.get('name')
        qs = User.objects.filter(is_active=True, is_delete=False)
        if academy:
            qs = qs.filter(academy__contains=academy)
        if name:
            qs = qs.filter(name__contains=name)

        return qs



class AdminCreateView(RootRequiredMixin, CreateView):
    """新增管理员"""
    model = User
    context_object_name = "user"
    template_name = "users/admin_create.html"
    form_class = UserForm

    def form_valid(self, form):
        """设置默认密码，用户名设置和邮箱相同"""
        pwd = Configration.objects.first().default_password
        form.instance.set_password(pwd)
        form.instance.username = form.instance.email
        form.instance.save()
        return super(AdminCreateView, self).form_valid(form)


    def get_success_url(self):
        messages.success(self.request, "新增管理员成功")
        return reverse("users:admins")


class AdminUpdateView(RootRequiredMixin, FormInitialMixin, UpdateView):
    """修改资料"""
    model = User
    context_object_name = "user"
    template_name = "users/admin_edit.html"
    form_class = UserForm

    def get_form(self, form_class=None):
        print(self.get_form_kwargs())
        return super(AdminUpdateView, self).get_form()

    def get_success_url(self):
        messages.success(self.request, "修改资料成功")
        return reverse_lazy("users:admins")


class AdminDeleteView(RootRequiredMixin, DeleteView):
    """删除管理员此操作需要ROOT权限"""
    model = User
    template_name = "users/admin_delete.html"
    context_object_name = "admin"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.is_delete = True
        self.object.save()
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        messages.warning(self.request, "删除管理员成功")
        return reverse_lazy("users:admins")


class MyDetailView(DetailView):
    """查看自己的资料"""
    model = User
    template_name = "users/admin_detail.html"
    context_object_name = "admin"

    def get_object(self, queryset=None):
        return self.request.user


class ApplyConfirmView(RootRequiredMixin, View):
    """批准用户注册为管理员需要ROOT权限"""
    def post(self, request):
        try:
            role_id = request.POST.get('role_id')
            username = request.POST.get('username')
            user = User.objects.get(username=username)
            user.role = role_id  # 增加用户权限
            user.register_success() # 审核通过
            send_user_verify_email(user.email)
            # 记录日志
            Log.objects.create(
                user=request.user,
                content=f"审核通过{user.name}的注册请求"
            )
        except Exception as e:
            return JsonResponse({"err": 1})
        return JsonResponse({"err": 0})

class DontApplyConfirmView(RootRequiredMixin, View):
    """不批准批准用户注册为管理员"""
    def post(self, request):
        try:
            user_id = request.POST.get('user_id')
            User.objects.get(pk=user_id).delete()
        except Exception as e:
            return JsonResponse({"err": 1})
        return JsonResponse({"err": 0})


class FreezeUserAPIView(RootRequiredMixin, View):
    """冻结或解冻账号"""
    def post(self, request):
        user_pk = request.POST.get("user_pk")
        user = get_user_model().objects.get(pk=user_pk)
        user.is_freeze = not user.is_freeze
        user.save()
        return JsonResponse({"status": "ok"})


class UserLogListAPIView(RootRequiredMixin, View):
    """查看管理员操作记录"""
    def get(self, request, pk):
        """
        :param pk: 用户pk
        """
        return_data = []
        logs = Log.objects.filter(user_id=pk)[:30]

        for log in logs:
            return_data.append({
                "time": log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "content": log.content,
            })

        return JsonResponse({"status": "ok", "count": len(return_data), "data": return_data})


# =======学院的增删改查========
academy_crud = CrudViewFactory('academy', 'academies', Academy,
                            {'role_required': (RoleEnum.ROOT.value, )}, (RootRequiredMixin,))
AcademyList = academy_crud.create_list_view()
AcademyCreate = academy_crud.create_create_view(True, 0, "新增学院成功", 'academy')
AcademyDelete = academy_crud.create_delete_view("删除学院成功", "academy")
AcademyUpdate = academy_crud.create_update_view(True, 0, '修改学院成功', 'academy')

# =======年级的增删改查========
grade_crud = CrudViewFactory('grade', 'grades', Grade,
                            {'role_required': (RoleEnum.ROOT.value, )}, (RootRequiredMixin,))
GradeList = grade_crud.create_list_view()
GradeCreate = grade_crud.create_create_view(True, 0, "新增年级成功", 'grade')
GradeDelete = grade_crud.create_delete_view("删除年级成功", "grade")
GradeUpdate = grade_crud.create_update_view(True, 0, '修改年级成功', 'grade')
# =======协会的增删改查========
institute_crud = CrudViewFactory('institute', 'institutes', Institute,
                            {'role_required': (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value)}, (RoleRequiredMixin,))
InstituteList = institute_crud.create_list_view()
class InstituteCreate(RoleRequiredMixin, CreateView):
    template_name = "institute/create.html"
    form_class = InstituteForm
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value)
    context_object_name = "institute"
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.save()
        return super().form_valid(form)
    def get_success_url(self):
        messages.success(self.request, "新增协会成功")
        return reverse("institute")
InstituteDelete = institute_crud.create_delete_view("删除协会成功", "institute")
InstituteUpdate = institute_crud.create_update_view(False, InstituteForm, '修改协会成功', 'institute')
