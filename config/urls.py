from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.views import defaults as default_views
from rest_framework.routers import DefaultRouter

from learntime.activity.views import StoreDetailViewSet
from learntime.student.views import find_student_by_uid_and_name
from learntime.users.views import IndexView, AcademyList, AcademyCreate, AcademyUpdate, AcademyDelete


router = DefaultRouter()
router.register("activities", StoreDetailViewSet, base_name="activities")

urlpatterns = [

    path("api/", include(router.urls)),
    path("",  IndexView.as_view(), name='index'),

    #学院管理
    path("academy/", AcademyList.as_view(), name="academy"),
    path("academy/create/", AcademyCreate.as_view(), name="academy_create"),
    path("academy/update/<int:pk>/", AcademyUpdate.as_view(), name="academy_update"),
    path("academy/delete/<int:pk>/", AcademyDelete.as_view(), name="academy_delete"),

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
