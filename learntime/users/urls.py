from django.urls import path

from learntime.users.views import (
    login_view, logout_view)

app_name = "users"
urlpatterns = [
    path("login/", view=login_view, name='login'),
    path('logout/', view=logout_view, name='logout')
]
