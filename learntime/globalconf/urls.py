from django.urls import path

from learntime.globalconf import views

app_name = "conf"
urlpatterns = [
    path("show/", view=views.ConfDetailView.as_view(), name="show"),
    path("edit/<int:pk>/", view=views.ConfEditView.as_view(), name="edit"),
    path("remove-session/", view=views.RemoveSessionView.as_view(), name='remove_session'),
    path("maintenance/", view=views.MaintenanceSystemView.as_view(), name='maintenance'),
    path("help/list/", view=views.HelpListView.as_view(), name="help_list"),
    path("help/create/", view=views.HelpCreateView.as_view(), name="help_create"),
    path("help/detail/<int:pk>/", view=views.HelpDetailView.as_view(), name="help_detail"),
    path("help/update/<int:pk>/", view=views.HelpUpdateView.as_view(), name="help_update"),
    path("help/delete/<int:pk>/", view=views.HelpDeleteView.as_view(), name="help_delete"),


    path("gzcc/", view=views.GZCCView.as_view(), name="gzcc")
]
