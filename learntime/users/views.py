from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.views.generic import ListView, DetailView

from learntime.users.forms import LoginForm, RegisterForm

User = get_user_model()

def login_view(request):
    """登录视图"""
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
    """注销视图"""
    logout(request)
    return redirect(reverse_lazy("users:login"))



def register_view(request):
    """注册"""
    if request.method == "GET":
        form = RegisterForm()
        return render(request, 'users/register.html', {'form': form})
    elif request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = User(
                username=form.cleaned_data['username'],
                email = form.cleaned_data['email'],
                name = form.cleaned_data['name'],
                identity = form.cleaned_data['identity'],
            )
            user.set_password(form.cleaned_data['password'])
            user.register()
            return render(request, 'users/register_success.html')

        return render(request, 'users/register.html', {'form': form})


class AdminApplyList(PermissionRequiredMixin, ListView):
    template_name = "users/admin_apply.html"
    context_object_name = "admins"
    paginate_by = 20
    permission_required = ("add_user", "change_user", "delete_user", "view_user")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        groups = Group.objects.all().prefetch_related("permissions")
        context['groups'] = groups
        return context


    def get_queryset(self):
        return User.objects.filter(is_active=False)


class AdminList(AdminApplyList):
    template_name = "users/admin_list.html"

    def get_queryset(self):
        return User.objects.filter(is_active=True)


class AdminDetail(PermissionRequiredMixin, DetailView):
    """管理员详情页"""

    permission_required = ("view_user")
    context_object_name = 'admin'
    template_name = "users/admin_detail.html"
    model = User


