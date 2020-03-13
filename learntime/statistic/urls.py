from django.urls import path

from learntime.statistic import views

app_name = "stat"
urlpatterns = [
    path("rank_chart/", views.rank_chart_view, name='rank_chart'),
    path('', views.StatisticView.as_view(), name='stat')
]
