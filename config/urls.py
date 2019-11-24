from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.views import defaults as default_views

from learntime.student.views import find_student_by_uid_and_name
from learntime.users.views import AcademyList, AcademyCreate, AcademyUpdate, AcademyDelete, GradeList, \
    GradeCreate, GradeDelete, GradeUpdate
from statistic.views import IndexView, chart_view

urlpatterns = [
    path("",  IndexView.as_view(), name='index'),
    path("chart/", chart_view, name='chart'),

    #学院管理
    path("academy/", AcademyList.as_view(), name="academy"),
    path("academy/create/", AcademyCreate.as_view(), name="academy_create"),
    path("academy/update/<int:pk>/", AcademyUpdate.as_view(), name="academy_update"),
    path("academy/delete/<int:pk>/", AcademyDelete.as_view(), name="academy_delete"),

    #年级管理
    path("grade/", GradeList.as_view(), name="grade"),
    path("grade/create/", GradeCreate.as_view(), name="grade_create"),
    path("grade/update/<int:pk>/", GradeUpdate.as_view(), name="grade_update"),
    path("grade/delete/<int:pk>/", GradeDelete.as_view(), name="grade_delete"),

    path("users/", include("learntime.users.urls", namespace="users")),
    path("students/", include("learntime.student.urls", namespace="students")),
    path("activities/", include("learntime.activity.urls", namespace="activities")),
    path("logs/", include("learntime.operation.urls", namespace="logs")),

    path('ckeditor/', include('learntime.utils.ckeditor_urls')),


    # 临时接口
    path("api/find_student/", find_student_by_uid_and_name)


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:

    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
