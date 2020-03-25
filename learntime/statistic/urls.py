from django.urls import path

from learntime.statistic import views

app_name = "stat"
urlpatterns = [
    path("rank_chart/<int:maximum>/", views.rank_chart_view, name='rank_chart'),
    path("class_average_credit_chart/", views.class_average_credit_view, name='class_average_credit_chart'),
    path("grade_average_credit_change_per_month_chart/", views.grade_average_credit_change_per_month_view, name='grade_average_credit_change_per_month_chart'),
    path('', views.StatisticView.as_view(), name='stat')
]
