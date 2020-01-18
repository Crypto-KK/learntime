import json

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.base import View
from django.db.models import Q

from io import BytesIO
import xlrd

from config.settings.base import CREDIT_TYPE
from learntime.operation.models import Log
from learntime.student.forms import StudentExcelForm, StudentCreateForm, StudentEditForm, StudentCreditCreateForm
from learntime.student.models import Student, StudentCreditVerify
from learntime.users.enums import RoleEnum
from learntime.users.models import Academy
from learntime.utils.helpers import RoleRequiredMixin, PaginatorListView, FormInitialMixin, \
    RootRequiredMixin, add_credit, add_student_activity

success = JsonResponse({"status": "ok"})
fail = JsonResponse({"status": "fail"})
User = get_user_model()

class StudentList(RoleRequiredMixin, PaginatorListView):
    """学生列表页

    需要ROOT、校级、学院级的权限
    """
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value, RoleEnum.ACADEMY.value)
    template_name = "students/student_list.html"
    paginate_by = 20
    context_object_name = "students"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        academies = Academy.objects.values_list("name")
        context['academy_list'] = [name[0] for name in academies]
        context['form'] = StudentExcelForm()
        return context

    def get_queryset(self):
        """按照不同权限查看不同的学生"""
        role = self.request.user.role
        uid = self.request.GET.get('uid')
        name = self.request.GET.get('name')
        academy = self.request.GET.get('academy')
        grade = self.request.GET.get('grade')
        clazz = self.request.GET.get('clazz')

        # 初步的students查询集
        students = Student.objects.filter(
            academy=self.request.user.academy) \
            if role == RoleEnum.ACADEMY.value else Student.objects.all()

        if uid:
            return students.filter(uid=uid)
        if name:
            return students.filter(name__contains=name)
        if academy:
            return students.filter(academy__contains=academy)
        if grade:
            return students.filter(grade__contains=grade)
        if clazz:
            return students.filter(clazz__contains=clazz)

        return students


class StudentDetail(RoleRequiredMixin, DetailView):
    """学生详情"""
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value, RoleEnum.ACADEMY.value)
    context_object_name = "student"
    template_name = "students/student_detail.html"
    model = Student


class StudentCreate(RootRequiredMixin, CreateView):
    """添加学生"""
    model = Student
    template_name = "students/student_create.html"
    form_class = StudentCreateForm

    def form_valid(self, form):
        # 添加日志
        Log.objects.create(
            user=self.request.user,
            content=f"添加了学生<{form.instance.name}>"
        )
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "添加学生成功")
        return reverse_lazy("students:students")


class StudentUpdate(RootRequiredMixin, FormInitialMixin, UpdateView):
    """修改学生"""
    model = Student
    form_class = StudentEditForm
    template_name = "students/student_update.html"
    context_object_name = "student"

    def form_valid(self, form):
        # 添加日志
        Log.objects.create(
            user=self.request.user,
            content=f"修改了学生<{form.instance.name}>"
        )
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "修改学生成功")
        return reverse_lazy("students:students")


class StudentDelete(RootRequiredMixin, DeleteView):
    """删除学生"""
    model = Student
    template_name = "students/student_delete.html"
    context_object_name = "student"

    def get_success_url(self):
        messages.success(self.request, "删除学生成功")
        return reverse_lazy("students:students")


class StudentExcelImportView(RootRequiredMixin, View):
    """学生excel导入视图"""

    def post(self, request):
        form = StudentExcelForm(request.POST, request.FILES) # 获取提交后的表单
        if form.is_valid(): # 表单校验通过
            #StudentFile.objects.create(excel_file=form.cleaned_data['excel_file'])
            file_obj = request.FILES['excel_file'].read()
            try:
                workbook = xlrd.open_workbook(file_contents=file_obj) # 使用xlrd打开excel文件
                print(workbook)
                table = workbook.sheets()[0] # 获取第一个工作薄
                nrows = table.nrows # 获取总行数
                for _ in range(1, nrows): # 从第二行开始导入数据
                    row = table.row_values(_) # 获取一条记录
                    student = Student.objects.create(
                        uid=row[0], name=row[1], academy=row[2],
                        grade=row[3], clazz=row[4], credit=float(row[5]),
                        wt_credit=float(row[6]), fl_credit=float(row[7]), xl_credit=float(row[8]),
                        cxcy_credit=float(row[9]), sxdd_credit=float(row[10])
                    ) # 创建一个学生实例
                    student.save() # 保存

            except Exception as e: # 文件内容有误
                print(e)
                return JsonResponse({"status": "fail", "reason": "导入失败！"})

            # 写入日志中
            Log.objects.create(
                user=self.request.user,
                content=f"导入了{nrows - 1}条学生记录"
            )
            return JsonResponse({"status": "ok"})

        else: # 文件格式错误
            return JsonResponse({"status": "fail", "reason": "必须为xls或xlsx格式！"})


class StudentExcelExportView(RootRequiredMixin, View):
    """学生excel导出视图"""

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

        # 写入日志
        Log.objects.create(
            user=self.request.user,
            content=f"下载了{row - 1}条学生记录"
        )

        return response


class StudentBulkDeleteView(RootRequiredMixin, View):
    """学生批量删除"""

    def post(self, request):
        try:
            student_list = request.POST['student_list'].split('-')
            for uid in student_list:
                Student.objects.get(pk=uid).delete()
            # 写入日志
            Log.objects.create(
                user=self.request.user,
                content=f"批量删除了{len(student_list)}条学生记录"
            )
            return JsonResponse({"status": "ok"})
        except Exception:
            return JsonResponse({"status": "fail"})


class StudentAllDeleteView(RootRequiredMixin, View):
    """学生全部删除"""
    def post(self, request):
        try:
            Student.objects.all().delete()
            # 写入日志
            Log.objects.create(
                user=self.request.user,
                content=f"删除了所有学生记录"
            )
        except Exception:
            return fail
        return success


class StudentCreditView(RoleRequiredMixin, PaginatorListView):
    """学生学时列表页
    权限：root和学院
    """
    role_required = (RoleEnum.ROOT.value, RoleEnum.ACADEMY.value)
    template_name = 'students/student_credit.html'
    paginate_by = 20
    context_object_name = 'students'

    def get_queryset(self):
        _get = self.request.GET.get
        role = self.request.user.role
        # 获取条件查询参数
        uid, name, academy, grade, clazz = _get('uid'), _get('name'), \
                                           _get('academy'), _get('grade'), _get('clazz')

        # 初步的students查询集
        students = Student.objects.all()
        if role == RoleEnum.ACADEMY.value:
            students = students.filter(academy=self.request.user.academy)

        if uid:
            return students.filter(uid=uid)
        if name:
            return students.filter(name__contains=name)
        if academy:
            return students.filter(academy__contains=academy)
        if grade:
            return students.filter(grade__contains=grade)
        if clazz:
            return students.filter(clazz__contains=clazz)

        return students


class StudentEditCreditView(RoleRequiredMixin, View):
    """根据学号查询和修改某个学生的学时
    权限：root和院级
    """
    role_required = (RoleEnum.ROOT.value, RoleEnum.ACADEMY.value)

    def get(self, request):
        """获取当前学生的所有学时信息并渲染到表单上"""
        uid = request.GET.get('uid')
        if uid:
            student = Student.objects.get(pk=uid)
            return JsonResponse({
                "status": "ok",
                "name": student.name,
                "wt_credit": student.wt_credit,
                "fl_credit": student.fl_credit,
                "xl_credit": student.xl_credit,
                "cxcy_credit": student.cxcy_credit,
                "sxdd_credit": student.sxdd_credit,
            })
        return fail

    def post(self, request):
        """修改当前学生的学时"""
        get = request.POST.get
        uid = get('uid')
        wt_credit = get('wt_credit')
        fl_credit = get('fl_credit')
        xl_credit = get('xl_credit')
        cxcy_credit = get('cxcy_credit')
        sxdd_credit = get('sxdd_credit')

        if uid:
            student = Student.objects.get(pk=uid)
            previous_credit = student.credit
            student.wt_credit = float(wt_credit)
            student.fl_credit = float(fl_credit)
            student.xl_credit = float(xl_credit)
            student.cxcy_credit = float(cxcy_credit)
            student.sxdd_credit = float(sxdd_credit)
            student.save()
            current_credit = student.credit
            amount_credit = current_credit - previous_credit
            op = ""
            if amount_credit == 0:
                op = "无变化"
            if amount_credit > 0:
                op = f"增加{amount_credit}"
            elif amount_credit < 0:
                op = f'减少{-amount_credit}'
            # 写入日志
            Log.objects.create(
                user=self.request.user,
                content=f"修改了<{student.uid}>{student.name}的学时，总学时{op}"
            )
            return JsonResponse({
                "status": "ok",
                "name": student.name,
            })
        return fail


class StudentBulkAddCreditView(RoleRequiredMixin, View):
    """批量增加某个班级所有学生的学时
    权限：root和院级
    """
    role_required = (RoleEnum.ROOT.value, RoleEnum.ACADEMY.value)
    def post(self, request):
        _get = request.POST.get
        # 学时类别，增量，班级
        _type, amount, clazz = _get('_type'), _get('amount'), _get('clazz')
        real_clazz = ''
        credit_map = {
            "wt_credit": "文体学时",
            "fl_credit": "法律学时",
            "xl_credit": "心理学时",
            "cxcy_credit": "创新创业学时",
            "sxdd_credit": "思想道德学时",
        }
        try:
            # 模糊查询班级
            for student in Student.objects.filter(clazz__contains=clazz):
                if not real_clazz:
                    real_clazz = student.clazz
                # 设置学生的某学时
                setattr(student, _type, getattr(student, _type) + float(amount))
                student.save()
            # 记录日志
            Log.objects.create(
                user = self.request.user,
                content = f'批量增加了{real_clazz}所有学生的{credit_map[_type]} {amount}分'
            )
        except Exception:
            return fail
        return success


class StudentCreditApplyListView(RoleRequiredMixin, PaginatorListView):
    """学时补录申请列表页
    权限：学生干部级
    """
    role_required = (RoleEnum.STUDENT.value, RoleEnum.ACADEMY.value)
    paginate_by = 50
    context_object_name = "students"
    template_name = "students/student_credit_apply_list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        tos = User.objects.filter(role=RoleEnum.ACADEMY.value) # 院级审核者
        context['tos'] = tos
        context['form'] = StudentExcelForm()
        return context

    def get_queryset(self):
        return StudentCreditVerify.objects.filter(verify=False, user=self.request.user)


class StudentCreditApplyConfirmListView(RoleRequiredMixin, PaginatorListView):
    """学时补录审核成功列表页
    权限：学生干部级
    """
    role_required = (RoleEnum.STUDENT.value, RoleEnum.ACADEMY.value)
    paginate_by = 50
    context_object_name = "students"
    template_name = "students/student_credit_confirm_list.html"

    def get_queryset(self):
        # 显示自己提交并且审核通过的补录申请或者自己审核通过的申请
        return StudentCreditVerify.objects.filter(verify=True).filter(Q(user=self.request.user) | Q(to=self.request.user))




class StudentCreditApplyCreateView(RoleRequiredMixin, CreateView):
    """添加补录数据
        权限：学生干部级
    """
    model = Student
    template_name = "students/student_credit_apply_create.html"
    form_class = StudentCreditCreateForm
    role_required = (RoleEnum.STUDENT.value,)

    def form_valid(self, form):
        # 添加日志
        Log.objects.create(
            user=self.request.user,
            content=f"学时补录<{form.instance.uid} - {form.instance.name} 增加{form.instance.credit}学时>已提交<{form.instance.to.name}>审核"
        )
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "添加补录数据成功")
        return reverse_lazy("students:student_credit_apply")


class StudentCreditExcelImportView(RoleRequiredMixin, View):
    """导入学时补录数据接口"""
    role_required = (RoleEnum.STUDENT.value, RoleEnum.ACADEMY.value)
    def post(self, request):
        form = StudentExcelForm(request.POST, request.FILES) # 获取提交后的表单
        if form.is_valid(): # 表单校验通过
            to_id = request.POST.get("to_id")
            try:
                to = User.objects.get(pk=to_id)
            except User.DoesNotExist:# 如果查询不到审核者，直接报错
                if request.user.role == RoleEnum.ACADEMY.value:
                    to = request.user
                    print(to)
                else:
                    return JsonResponse({"status": "fail", "reason": "请选择审核者"})

            try:
                workbook = xlrd.open_workbook(file_contents=request.FILES['excel_file'].read()) # 使用xlrd打开excel文件
                table = workbook.sheets()[0] # 获取第一个工作薄
                nrows = table.nrows # 获取总行数
                for _ in range(2, nrows): # 从第3行开始导入数据
                    row = table.row_values(_) # 获取一条记录
                    obj = StudentCreditVerify.objects.create(
                        activity_name=row[0], sponsor=row[1], name=row[2],
                        uid=row[3], academy=row[4], clazz=row[5],
                        join_type=row[6], award=row[7], credit_type=row[8],
                        credit=row[9], contact=row[10], to_name=row[11],
                        to=to, user=request.user
                    )
                    if obj.to == obj.user: # 审核者和申请者相同,增加学时
                        obj.verify = True
                        if not add_credit(CREDIT_TYPE, obj.uid, obj.credit_type, obj.credit):
                            return JsonResponse({"status": "fail", "reason": "增加学时失败"})
                        if not add_student_activity(obj.uid, obj.join_type,
                                                    activity_name=obj.activity_name,
                                                    credit=obj.credit,
                                                    credit_type=obj.credit_type):
                            return JsonResponse({"status": "fail", "reason": "学生活动关联失败"})
                        obj.save()

            except Exception as e: # 文件内容有误
                print(e)
                return JsonResponse({"status": "fail", "reason": e.__str__()})

            # 写入日志中
            Log.objects.create(
                user=self.request.user,
                content=f"导入了{nrows - 1}条需要增加学时的学生记录，等待审核中"
            )
            return JsonResponse({"status": "ok"})

        else: # 文件格式错误
            return JsonResponse({"status": "fail", "reason": "必须为xls或xlsx格式！"})


class StudentCreditDeleteView(RoleRequiredMixin, View):
    """学时补录申请删除"""
    role_required = (RoleEnum.STUDENT.value, RoleEnum.ACADEMY.value)
    def post(self, request):
        try:
            pks = json.loads(request.POST.get("pks"))
            for pk in pks:
                obj = StudentCreditVerify.objects.get(pk=pk)
                obj.delete()
        except Exception as e:
            print(e)
            return JsonResponse({"status": "fail"})
        return JsonResponse({"status": "ok"})


class StudentCreditConfirmView(RoleRequiredMixin, View):
    """学时补录申请审核通过，需要院级权限"""
    role_required = (RoleEnum.ACADEMY.value,)
    def post(self, request):
        try:
            pks = json.loads(request.POST.get("pks"))
            for pk in pks:
                obj = StudentCreditVerify.objects.get(pk=pk)
                obj.verify = True
                obj.save()
                if not add_credit(CREDIT_TYPE, obj.uid, obj.credit_type, obj.credit):
                    return JsonResponse({"status": "fail", "reason": "增加学时失败"})
                if not add_student_activity(obj.uid, obj.join_type,
                                            activity_name=obj.activity_name,
                                            credit=obj.credit,
                                            credit_type=obj.credit_type):
                    return JsonResponse({"status": "fail", "reason": "学生与活动关联失败"})
        except Exception as e:
            print(e)
            return JsonResponse({"status": "fail"})
        return JsonResponse({"status": "ok"})


class StudentCreditVerifyListView(RoleRequiredMixin, PaginatorListView):
    """学生组织审核学时列表页
    权限：院级和学生组织
    """
    role_required = (RoleEnum.ACADEMY.value,)
    paginate_by = 50
    context_object_name = "students"
    template_name = "students/student_credit_verify_list.html"

    def get_queryset(self):
        return self.request.user.waiting_to_verify_credits.filter(verify=False)


@csrf_exempt
def find_student_by_uid_and_name(request):
    if request.method == "POST":
        POST = json.loads(request.body.decode('utf-8'))
        uid = POST['uid']
        name = POST['name']
        if isinstance(uid, list):
            uid = POST['uid'][0]
        if isinstance(name, list):
            name = POST['name'][0]
        try:
            Student.objects.filter(uid=uid, name=name)[0]
        except Exception:
            return fail
        return success
