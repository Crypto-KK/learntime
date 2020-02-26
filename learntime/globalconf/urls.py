from django.urls import path

from learntime.globalconf import views

app_name = "conf"
urlpatterns = [
    path("show/", view=views.ConfDetailView.as_view(), name="show"),
    path("edit/<int:pk>/", view=views.ConfEditView.as_view(), name="edit")
]
