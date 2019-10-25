from functools import wraps

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.http import HttpResponseBadRequest
from django.views.generic.base import View

from learntime.users.enums import RoleEnum


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


class RoleRequiredMixin(View):
    """角色权限控制"""
    role_required = ()

    def get_role_required(self):
        """
        重写该方法必须返回一个可迭代对象
        """
        if self.role_required is None:
            raise ImproperlyConfigured(
                '{0} is missing the role_required attribute. Define {0}.role_required, or override '
                '{0}.role_required().'.format(self.__class__.__name__)
            )
        if isinstance(self.role_required, str):
            roles = (self.role_required,)
        else:
            roles = self.role_required
        return roles


    def has_permission(self):

        roles = self.get_role_required()
        if self.request.user.role in roles:
            return True
        return False

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            raise PermissionDenied("没有权限")
        return super().dispatch(request, *args, **kwargs)


class RootRequiredMixin(RoleRequiredMixin):
    role_required = (RoleEnum.ROOT.value, )


class SchoolRequiredMixin(RoleRequiredMixin):
    role_required = (RoleEnum.SCHOOL.value, )


class AcademyRequiredMixin(RoleRequiredMixin):
    role_required = (RoleEnum.ACADEMY.value, )


class StudentRequiredMixin(RoleRequiredMixin):
    role_required = (RoleEnum.STUDENT.value,)
