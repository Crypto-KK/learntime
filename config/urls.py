from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views import defaults as default_views
from django.contrib.auth.decorators import login_required

admin.site.site_title = "学时通权限管理系统"
admin.site.site_header = "学时通权限管理系统"

urlpatterns = [
    path("",  login_required(TemplateView.as_view(template_name='front/index.html')), name='index'),

    path('testlogin', TemplateView.as_view(template_name='users/login.html'), name='log'),
    path('testregister', TemplateView.as_view(template_name='users/register.html'), name='reg'),

    path("users/", include("learntime.users.urls", namespace="users")),
    path("permission/", admin.site.urls)


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
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
