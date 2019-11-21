from django.contrib.auth.mixins import LoginRequiredMixin

from learntime.operation.models import Log
from learntime.utils.helpers import PaginatorListView


class LogList(LoginRequiredMixin, PaginatorListView):
    """日志列表页"""
    template_name = "operation/list.html"
    context_object_name = "logs"
    paginate_by = 20

    def get_queryset(self):
        if self.request.user.role == 1:
            return Log.objects.all().select_related("user")
        else:
            return Log.objects.filter(user=self.request.user).select_related("user")
