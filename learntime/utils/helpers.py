from functools import wraps

#from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.http import HttpResponseBadRequest
from django.views.generic import ListView
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
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not self.has_permission():
            raise PermissionDenied("没有权限")
        return super().dispatch(request, *args, **kwargs)


class PaginatorListView(ListView):
    """分页列表视图，默认左边和右边各5页"""
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        paginator = context['paginator']
        try:
            current_page = int(self.request.GET.get('page', 1))
        except Exception:
            current_page = 1

        if paginator.num_pages > 11:
            if current_page - 5 < 1:
                page_range = range(1, 11)
            elif current_page + 5 > paginator.num_pages:
                page_range = range(current_page - 5, paginator.num_pages + 1)
            else:
                page_range = range(current_page - 5, current_page + 6)
        else:
            page_range = paginator.page_range
        context['page_range'] = page_range
        return context
