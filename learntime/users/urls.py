from django.urls import path
from django.conf.urls import url

from learntime.users import views

app_name = "users"
urlpatterns = [
    path("login/", view=views.LoginView.as_view(), name='login'),
    path('logout/', view=views.logout_view, name='logout'),
    path('register/', view=views.RegisterView.as_view(), name='register'),

    # 变更邮箱url
    path('email/change/', view=views.EmailChangeView.as_view(), name='email_change'),

    # 忘记密码一系列url
    path('password/reset/', view=views.MyPasswordResetView.as_view(), name='password_reset'), # password_reset
    path('password/reset/done/', views.MyPasswordResetDoneView.as_view(), name='password_reset_done'),  # password_reset_done

    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        view=views.MyPasswordResetConfirmView.as_view(), name='password_reset_confirm'), # reset
    path('reset/done/', views.MyPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('password-change/', view=views.MyPasswordChangeView.as_view(), name='password_change'),
    path('password-change-done/', view=views.MyPasswordChangeDoneView.as_view(), name='password_change_done'),

    # 管理员管理功能
    path('admin_apply/', view=views.AdminApplyList.as_view(), name='admin_apply'),
    path('admins/', view=views.AdminList.as_view(), name='admins'),
    path('admin-create/', view=views.AdminCreateView.as_view(), name='admin_create'),
    path('admin-delete/<int:pk>/', view=views.AdminDeleteView.as_view(), name='admin_delete'),
    path('admin-update/<int:pk>/', view=views.AdminUpdateView.as_view(), name='update_profile'),
    path('my/', view=views.MyDetailView.as_view(), name='my_detail'),
    path("apply_confirm/", view=views.ApplyConfirmView.as_view(), name="apply_comfirm"),
    path("apply_no_confirm/", view=views.DontApplyConfirmView.as_view(), name="apply_no_comfirm"),

    # 冻结账号
    path("freeze/", view=views.FreezeUserAPIView.as_view(), name='freeze'),
    path("logs/<int:pk>/", view=views.UserLogListAPIView.as_view(), name='logs')
]
