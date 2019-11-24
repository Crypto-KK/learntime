from django.urls import path

from learntime.users.views import (
    login_view, logout_view, register_view, AdminApplyList, AdminList,
    AdminDetail, ApplyConfirmView, AdminUpdateView, AdminDeleteView, ForgetPwdView)

app_name = "users"
urlpatterns = [
    path("login/", view=login_view, name='login'),
    path('logout/', view=logout_view, name='logout'),
    path('register/', view=register_view, name='register'),
    path('forgot/', view=ForgetPwdView.as_view(), name='forgot_pwd'),

    path('admin_apply/', view=AdminApplyList.as_view(), name='admin_apply'),
    path('admins/', view=AdminList.as_view(), name='admins'),
    path('admin-detail/<int:pk>/', view=AdminDetail.as_view(), name='admin_detail'),
    path('admin-delete/<int:pk>/', view=AdminDeleteView.as_view(), name='admin_delete'),
    path('admin-update/<int:pk>/', view=AdminUpdateView.as_view(), name='update_profile'),
    path("apply_comfirm/", view=ApplyConfirmView.as_view(), name="apply_comfirm"),
]
