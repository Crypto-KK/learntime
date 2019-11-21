from django.urls import path

from learntime.activity import views

app_name = "activities"
urlpatterns = [
    # 我发布的活动
    path('', view=views.MyActivityList.as_view(), name='activities'),
    # 等待我审核的活动
    path('activity-unverify/', view=views.ActivityUnVerifyList.as_view(), name='activity_unverify'),
    # 我审核通过的活动
    path('activity-verify/', view=views.ActivityVerifyList.as_view(), name='activity_verify'),

    # 全部活动
    path('all/', view=views.AllActivityList.as_view(), name='activity_all'),

    # 新增活动
    path('create/', view=views.ActivityCreate.as_view(), name='activity_create'),
    # 活动详情
    path('detail/<str:pk>/', view=views.ActivityDetail.as_view(), name='activity_detail'),
    # 更新活动
    path('update/<str:pk>/', view=views.ActivityUpdate.as_view(), name='activity_update'),

    # 审核通过地址
    path("verify/", view=views.ActivityVerifyView.as_view(), name='verify'),

    # 审核不通过地址
    path("verify-fail/", view=views.ActivityVerifyFailView.as_view(), name='verify_fail'),

    # 审核向上级传递地址
    path("pass-verify/", view=views.ActivityPassVerifyView.as_view(), name='pass_verify'),

    # 根据学院获取管理员地址
    path("get-admins/", view=views.GetAdminsView.as_view(), name='get_admins')

]
