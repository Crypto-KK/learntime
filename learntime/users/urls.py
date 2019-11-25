from django.urls import path
from django.conf.urls import url

from learntime.users.views import (
    login_view, logout_view, register_view, AdminApplyList, AdminList,
    AdminDetail, ApplyConfirmView, AdminUpdateView, AdminDeleteView, MyPasswordResetView,
    MyPasswordResetConfirmView, MyPasswordResetDoneView)

app_name = "users"
urlpatterns = [
    path("login/", view=login_view, name='login'),
    path('logout/', view=logout_view, name='logout'),
    path('register/', view=register_view, name='register'),

    path('forgot/', view=MyPasswordResetView.as_view(), name='forgot_pwd'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        view=MyPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', MyPasswordResetDoneView.as_view(), name='password_reset_done'),

    path('admin_apply/', view=AdminApplyList.as_view(), name='admin_apply'),
    path('admins/', view=AdminList.as_view(), name='admins'),
    path('admin-detail/<int:pk>/', view=AdminDetail.as_view(), name='admin_detail'),
    path('admin-delete/<int:pk>/', view=AdminDeleteView.as_view(), name='admin_delete'),
    path('admin-update/<int:pk>/', view=AdminUpdateView.as_view(), name='update_profile'),
    path("apply_comfirm/", view=ApplyConfirmView.as_view(), name="apply_comfirm"),
]
