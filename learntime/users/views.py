from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login, logout

from learntime.users.forms import LoginForm

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
