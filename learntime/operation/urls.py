from django.urls import path

from learntime.operation import views

app_name = "logs"
urlpatterns = [
    path('', view=views.LogList.as_view(), name='list'),
]
