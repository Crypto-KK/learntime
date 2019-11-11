from django.urls import path

from learntime.activity import views

app_name = "activities"
urlpatterns = [

    path('', view=views.ActivityList.as_view(), name='activities'),
    path('activity-unverify/', view=views.ActivityUnVerifyList.as_view(), name='activity_unverify'),
    path('activity-verify/', view=views.ActivityVerifyList.as_view(), name='activity_verify'),
    path('create/', view=views.ActivityCreate.as_view(), name='activity_create'),
    path('detail/<str:pk>/', view=views.ActivityDetail.as_view(), name='activity_detail'),
    path('update/<str:pk>/', view=views.ActivityUpdate.as_view(), name='activity_update'),
    path("verify/", view=views.ActivityVerifyView.as_view(), name='verify'),
    path("get-admins/", view=views.GetAdminsView.as_view(), name='get_admins')
]
