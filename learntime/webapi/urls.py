from django.urls import path


from learntime.webapi import views
app_name = "webapi"
from rest_framework_jwt.views import obtain_jwt_token
urlpatterns = [
    path("login/", views.login_view, name="login"),
]
