from django.urls import path

from learntime.users.views import (
    login_view, logout_view, register_view, AdminApplyList, AdminList,
    AdminDetail, apply_comfirm, AdminUpdateView)

app_name = "users"
urlpatterns = [
    path("login/", view=login_view, name='login'),
    path('logout/', view=logout_view, name='logout'),
    path('register/', view=register_view, name='register'),

    path('admin_apply/', view=AdminApplyList.as_view(), name='admin_apply'),
    path('admins/', view=AdminList.as_view(), name='admins'),
    path('admin-detail/<int:pk>/', view=AdminDetail.as_view(), name='admin_detail'),
    path("apply_comfirm/", view=apply_comfirm, name="apply_comfirm"),
    path("update_profile/<int:pk>/", view=AdminUpdateView.as_view(), name="update_profile")
]
