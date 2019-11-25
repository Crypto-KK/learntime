from django.urls import path
from django.conf.urls import url

from learntime.users.views import (
    logout_view, AdminApplyList, AdminList,
    AdminDetail, ApplyConfirmView, AdminUpdateView, AdminDeleteView, MyPasswordResetView,
    MyPasswordResetConfirmView, MyPasswordResetDoneView, LoginView, RegisterView,
    MyPasswordResetCompleteView, MyPasswordChangeView, MyPasswordChangeDoneView, DontApplyConfirmView)

app_name = "users"
urlpatterns = [
    path("login/", view=LoginView.as_view(), name='login'),
    path('logout/', view=logout_view, name='logout'),
    path('register/', view=RegisterView.as_view(), name='register'),

    # 忘记密码一系列url
    path('password/reset/', view=MyPasswordResetView.as_view(), name='password_reset'), # password_reset
    path('password/reset/done/', MyPasswordResetDoneView.as_view(), name='password_reset_done'),  # password_reset_done

    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        view=MyPasswordResetConfirmView.as_view(), name='password_reset_confirm'), # reset
    path('reset/done/', MyPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('password-change/', view=MyPasswordChangeView.as_view(), name='password_change'),
    path('password-change-done/', view=MyPasswordChangeDoneView.as_view(), name='password_change_done'),

    # 管理员管理功能
    path('admin_apply/', view=AdminApplyList.as_view(), name='admin_apply'),
    path('admins/', view=AdminList.as_view(), name='admins'),
    path('admin-detail/<int:pk>/', view=AdminDetail.as_view(), name='admin_detail'),
    path('admin-delete/<int:pk>/', view=AdminDeleteView.as_view(), name='admin_delete'),
    path('admin-update/<int:pk>/', view=AdminUpdateView.as_view(), name='update_profile'),
    path("apply_confirm/", view=ApplyConfirmView.as_view(), name="apply_comfirm"),
    path("apply_no_confirm/", view=DontApplyConfirmView.as_view(), name="apply_no_comfirm"),
]
