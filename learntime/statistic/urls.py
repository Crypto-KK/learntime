from django.urls import path

from learntime.statistic import views

app_name = "stat"
urlpatterns = [
    path('', view=views.index, name='stat'),
]
