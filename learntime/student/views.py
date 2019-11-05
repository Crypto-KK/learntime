from django.conf import settings
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.base import View

from io import StringIO, BytesIO

from learntime.student.forms import StudentForm, StudentExcelForm
from learntime.student.models import Student, StudentFile
from learntime.users.enums import RoleEnum
from learntime.utils.helpers import RoleRequiredMixin


class StudentList(RoleRequiredMixin, ListView):
    """学生列表页

    需要ROOT、校级、学院级的权限
    """
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value, RoleEnum.ACADEMY.value)
    template_name = "students/student_list.html"
    paginate_by = 10
    context_object_name = "students"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        academy_name_list = []
        academy_list = Student.objects.all().values("academy").annotate(
            count=Count("academy"))
        for academy_dict in academy_list:
            academy_name_list.append(academy_dict['academy'])
        context['academy_list'] = list(set(academy_name_list))
        context['form'] = StudentExcelForm()
        return context

    def get_queryset(self):
        """按照不同权限查看不同的学生"""
        role = self.request.user.role
        if role == RoleEnum.ROOT.value or role == RoleEnum.SCHOOL.value:
            if self.request.GET.get('uid', None) is not None:
                return Student.objects.filter(uid=self.request.GET['uid'])
            return Student.objects.all()
        elif role == RoleEnum.ACADEMY.value:
            return Student.objects.filter(academy=self.request.user.academy)
        else:
            return Student.objects.none()


class StudentDetail(RoleRequiredMixin, DetailView):
    """学生详情"""

    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value, RoleEnum.ACADEMY.value)
    context_object_name = "student"
    template_name = "students/student_detail.html"
    model = Student


class StudentCreate(RoleRequiredMixin, CreateView):
    """添加学生"""
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value)
    model = Student
    template_name = "students/student_create.html"
    form_class = StudentForm


    def get_success_url(self):
        return reverse("students:students")


class StudentUpdate(RoleRequiredMixin, UpdateView):
    """修改学生"""
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value)
    model = Student
    form_class = StudentForm
    template_name = "students/student_update.html"
    context_object_name = "student"

    def get_success_url(self):
        return reverse("students:students")


class StudentDelete(RoleRequiredMixin, DeleteView):
    """删除学生"""
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value)
    model = Student
    template_name = "students/student_delete.html"
    context_object_name = "student"

    def get_success_url(self):
        return reverse("students:students")


class StudentExcelImportView(RoleRequiredMixin, View):
    """学生excel导入视图"""
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value)

    def post(self, request):
        form = StudentExcelForm(request.POST, request.FILES) # 获取提交后的表单
        if form.is_valid(): # 表单校验通过
            excel_file = form.cleaned_data['excel_file'] # 获取excel文件字段
            file_obj = StudentFile.objects.create(excel_file=excel_file) # 获取数据库记录

            import xlrd
            excel_file_name = settings.MEDIA_ROOT + "/" + str(file_obj.excel_file) # 生成文件路径
            try:
                workbook = xlrd.open_workbook(excel_file_name) # 使用xlrd打开excel文件
                table = workbook.sheets()[0] # 获取第一个工作薄
                nrows = table.nrows # 获取总行数
                for _ in range(1, nrows): # 从第二行开始导入数据
                    row = table.row_values(_) # 获取一条记录
                    student = Student.objects.create(
                        uid=row[0], name=row[1], academy=row[2],
                        grade=row[3], clazz=row[4], credit=row[5],
                        wt_credit=row[6], fl_credit=row[7], xl_credit=row[8],
                        cxcy_credit=row[9], sxdd_credit=row[10]
                    ) # 创建一个学生实例
                    student.save() # 保存

            except Exception as e: # 文件内容有误
                return JsonResponse({"status": "fail", "reason": "导入失败！"})

            return JsonResponse({"status": "ok"})

        else: # 文件格式错误
            return JsonResponse({"status": "fail", "reason": "必须为xls或xlsx格式！"})


class StudentExcelExportView(RoleRequiredMixin, View):
    """学生excel导出视图"""
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value)

    def get(self, request):
        import xlwt

        workbook = xlwt.Workbook(encoding="utf-8") # 创建workbook实例
        sheet = workbook.add_sheet("sheet1") # 创建工作薄1

        # 写标题栏
        sheet.write(0, 0, '学号')
        sheet.write(0, 1, '姓名')
        sheet.write(0, 2, '学院')
        sheet.write(0, 3, '年级')
        sheet.write(0, 4, '班级')
        sheet.write(0, 5, '总学时')
        sheet.write(0, 6, '文体学时')
        sheet.write(0, 7, '法律学时')
        sheet.write(0, 8, '心理学时')
        sheet.write(0, 9, '创新创业学时')
        sheet.write(0, 10, '思想道德学时')

        # 写数据
        row = 1
        for student in Student.objects.all(): # 单条写入学生数据
            sheet.write(row, 0, student.uid)
            sheet.write(row, 1, student.name)
            sheet.write(row, 2, student.academy)
            sheet.write(row, 3, student.grade)
            sheet.write(row, 4, student.clazz)
            sheet.write(row, 5, student.credit)
            sheet.write(row, 6, student.wt_credit)
            sheet.write(row, 7, student.fl_credit)
            sheet.write(row, 8, student.xl_credit)
            sheet.write(row, 9, student.cxcy_credit)
            sheet.write(row, 10, student.sxdd_credit)
            row += 1

        sio = BytesIO() # StringIO报错，使用BytesIO
        workbook.save(sio)
        sio.seek(0) # 定位到开始
        response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=students.xls'
        response.write(sio.getvalue())
        return response


@method_decorator(csrf_exempt, "dispatch")
class StudentBulkDeleteView(RoleRequiredMixin, View):
    """学生excel导出视图"""
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value)

    def post(self, request):
        try:
            student_list = request.POST['student_list'].split('-')
            for uid in student_list:
                student = Student.objects.get(pk=uid).delete()
            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "fail"})
