from django.urls import path

from learntime.operation import views

app_name = "operations"
urlpatterns = [
    path('logs/', view=views.LogList.as_view(), name='log_list'),
    path('join-list/', view=views.StudentActivityListView.as_view(), name='join_list'),
    path('sign-in-list/', view=views.SignInListView.as_view(), name='sign_in_list'),
    path('qrcode/', view=views.QRCodeAPIView.as_view(), name='qrcode'),
]
