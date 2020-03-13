from django.shortcuts import render

from learntime.globalconf.models import Configration

is_maintenance = None
maintenance_notice = None

class SystemMiddleware:
    """全局中间件"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global is_maintenance, maintenance_notice
        if is_maintenance == None:
            conf = Configration.objects.first()
            is_maintenance = conf.is_maintenance
            maintenance_notice = conf.maintenance_notice
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if is_maintenance and not request.user.is_superuser and not view_func.__name__ == "LoginView":
            # 除登录界面以外的页面，跳转到维护界面
            return render(request, "conf/maintenance.html", {"notice": maintenance_notice})
