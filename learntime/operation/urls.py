from django.urls import path

from learntime.operation import views

app_name = "operations"
urlpatterns = [
    path('logs', view=views.LogList.as_view(), name='log_list'),
    path('join_list', view=views.StudentActivityListView.as_view(), name='join_list'),
]
