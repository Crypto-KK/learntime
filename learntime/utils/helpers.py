from functools import wraps

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.http import HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, UpdateView
from django.views.generic.base import View

from learntime.users.enums import RoleEnum
from learntime.users.models import Grade, Academy
from learntime.student.models import Student
from django.conf import settings

disable_csrf = method_decorator(csrf_exempt, "dispatch")

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


class RoleRequiredMixin(LoginRequiredMixin, View):
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
    role_required = (RoleEnum.ROOT.value,)


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
        context['count'] = paginator.count
        return context


class FormInitialMixin(UpdateView):
    def get_initial(self):
        """获取学院和年级下拉列表的初始值"""
        obj = self.get_object()
        initial = super().get_initial()
        grade = Grade.objects.filter(name=obj.grade)
        academy = Academy.objects.filter(name=obj.academy)
        if len(grade):
            initial.update(grade=grade.get().pk)
        if len(academy):
            initial.update(academy=academy.get().pk)
        return initial.copy()



def add_credit(mappings, student_pk, credit_type, mount):
    """增加学时
    :param mappings: 映射
    :param student_pk: 学号
    :param credit_type: 学时类别，例如思想品德素质
    :param mount: 增加的学时
    :return 1 success
    """

    if not mappings:
        mappings = settings.CREDIT_TYPE
    try:
        student = Student.objects.get(pk=student_pk)
        credit_type = str(credit_type).strip()
        credit_type_attr = mappings[credit_type]
        old_credit = getattr(student, credit_type_attr)
        setattr(student, credit_type_attr, old_credit + float(mount))
        student.save()
    except Exception as e:
        print(e)
        return 0
    else:
        return 1


def minus_credit(mappings, student_pk, credit_type, mount):
    """减少学时
    :param mappings: 映射
    :param student_pk: 学号
    :param credit_type: 学时类别，例如思想品德素质
    :param mount: 增加的学时
    :return 1 success
    """
    try:
        student = Student.objects.get(pk=student_pk)
        credit_type_attr = mappings[credit_type]
        old_credit = getattr(student, credit_type_attr)
        setattr(student, credit_type_attr, old_credit - mount)
        student.save()
    except Exception as e:
        return 0
    else:
        return 1
