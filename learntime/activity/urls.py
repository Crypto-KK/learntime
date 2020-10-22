from django.urls import path

from learntime.activity import views

app_name = "activities"
urlpatterns = [
    # 根据学院获取管理员地址
    path("get-admins/", view=views.GetAdminsView.as_view(), name='get_admins')
]
