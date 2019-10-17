from functools import wraps

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.http import HttpResponseBadRequest
from django.views.generic.base import View


def ajax_required(func):
    '''
    验证是否为ajax请求
    :param func:
    :return:
    '''
    @wraps(func)
    def _wrapper(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest('ajax required')
        return func(request, *args, **kwargs)

    return _wrapper


class AuthorRequiredMixin(View):
    '''
    验证是否为作者
    '''
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.username != self.request.user.username:
            raise PermissionDenied()
        return super(AuthorRequiredMixin, self).dispatch(request, *args, **kwargs)


class GroupRequiredMixin(AccessMixin):
    """验证用户是否在该组中"""
    group_required = None

    def get_group_required(self):
        """
        重写该方法必须返回一个可迭代对象
        """
        if self.group_required is None:
            raise ImproperlyConfigured(
                '{0} is missing the group_required attribute. Define {0}.group_required, or override '
                '{0}.get_group_required().'.format(self.__class__.__name__)
            )
        if isinstance(self.group_required, str):
            groups = (self.group_required,)
        else:
            groups = self.group_required
        return groups

    def has_permission(self):
        """
        查询用户是否在该组中
        """
        groups = self.get_group_required()
        current_user_group_name = self.request.user.groups.all().prefetch_related("permissions")[0].name
        if current_user_group_name in groups:
            return True
        else:
            return False

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
