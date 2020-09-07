from django.urls import path

from learntime.operation import views

app_name = "operations"
urlpatterns = [

    path("send_email/", view=views.SendEmailAPIView.as_view(), name='send_email'),

    path('logs/', view=views.LogList.as_view(), name='log_list'),
    path('log-detail/<int:pk>/', view=views.LogDetail.as_view(), name='log_detail'),

    path('comments/', view=views.CommentList.as_view(), name='comment_list'),

    path('feedback/', view=views.FeedBackListView.as_view(), name='feedback_list'),
    path('feedback/create/', view=views.FeedBackCreateView.as_view(), name='feedback_create'),
    path('feedback/delete/<int:pk>/', view=views.FeedBackDeleteView.as_view(), name='feedback_delete'),
    path('feedback/detail/', view=views.FeedBackDetailAPIView.as_view(), name='feedback_detail'),

    path('join-list/', view=views.StudentActivityListView.as_view(), name='join_list'),
    # 导出学生参加活动记录
    path('join-list-export/', view=views.StudentActivityExportView.as_view(), name='join_list_export'),
    path('alter-status/', view=views.AlterStatusAPIView.as_view(), name='alter_status'),

    # 查看学生的参加活动记录
    path("join-record/", view=views.SearchRecordByPkAndTypeAPIView.as_view(), name='join_record'),

    path('sign-in-list/', view=views.SignInListView.as_view(), name='sign_in_list'),
    path('qrcode/<str:pk>/<int:frequency>/<int:signInOrSignOut>/<int:nonce>/', view=views.QRCodeAPIView.as_view(), name='qrcode'),
    path('person-list/<str:pk>/', view=views.PersonListAPIView.as_view(), name='person_list'),
]
