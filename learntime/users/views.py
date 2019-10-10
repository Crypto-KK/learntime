from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login, logout

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
    next = request.GET.get('next', '')
    if request.method == "GET":
        form = RegisterForm()
        return render(request, 'users/register.html', {'form': form})
    elif request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            print(form.cleaned_data)
            return JsonResponse({"error": "ok"})

        else:
            for err in form.errors:
                if err == "username":  # 用户名重复
                    return render(request, 'users/register.html', {
                        "form": form,
                        "error": "用户名重复,请重新输入"
                    })
                if err == "email":  # 邮箱重复
                    return render(request, 'users/register.html', {
                        "form": form,
                        "error": "邮箱重复,请重新输入"
                    })
                if err == "identity":
                    return render(request, 'users/register.html', {
                        "form": form,
                        "error": "请选择级"
                    })
