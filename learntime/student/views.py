import json

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction
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
from learntime.student.forms import StudentExcelForm, StudentCreateForm, StudentEditForm, StudentCreditCreateForm, \
    CreditApplyManuallyCreateView, CreditVerifyUpdateForm
from learntime.student.models import Student, StudentCreditVerify
from learntime.users.enums import RoleEnum
from learntime.users.models import Academy
from learntime.utils.helpers import RoleRequiredMixin, PaginatorListView, FormInitialMixin, \
    RootRequiredMixin, add_credit, add_student_activity, minus_credit, remove_student_activity
from utils.response_template import fail_response, success_response

User = get_user_model()

class StudentList(RoleRequiredMixin, PaginatorListView):
    """学生列表页

    需要ROOT、校级、学院级的权限
    """
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value, RoleEnum.ACADEMY.value, RoleEnum.ORG.value)
    template_name = "students/student_list.html"
    paginate_by = 50
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
        students = Student.objects.all()
        student_list = []
        if uid:
            students = students.filter(uid=uid)
        if name:
            students = students.filter(name__contains=name)
        if academy:
            students = students.filter(academy__contains=academy)
        if grade:
            students = students.filter(grade__contains=grade)
        if clazz:
            students = students.filter(clazz__contains=clazz)

        if role == RoleEnum.ACADEMY.value:
            students = students.filter(academy=self.request.user.academy,
                                       grade=self.request.user.grade)
            for student in students.filter(uid__startswith="{}".format(self.request.user.grade.split("级")[0])):
                # 将学号为当前辅导员年级的优先显示
                student_list.append(student)
            for student in students.exclude(uid__startswith="{}".format(self.request.user.grade.split("级")[0])):
                student_list.append(student)

        elif role == RoleEnum.ORG.value:
            students = students.filter(academy=self.request.user.academy)
            for student in students:
                student_list.append(student)

        else:
            for student in students:
                student_list.append(student)

        return student_list


class StudentDetail(RoleRequiredMixin, DetailView):
    """学生详情"""
    role_required = (RoleEnum.ROOT.value, RoleEnum.SCHOOL.value, RoleEnum.ACADEMY.value, RoleEnum.ORG.value)
    context_object_name = "student"
    template_name = "students/student_detail.html"
    model = Student


class StudentCreate(RoleRequiredMixin, CreateView):
    """添加学生"""
    role_required = (RoleEnum.ACADEMY.value, RoleEnum.ROOT.value, RoleEnum.ORG.value)
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


class StudentUpdate(RoleRequiredMixin, FormInitialMixin, UpdateView):
    """修改学生"""
    role_required = (RoleEnum.ROOT.value, RoleEnum.ACADEMY.value, RoleEnum.ORG.value, RoleEnum.SCHOOL.value)
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


class StudentDelete(RoleRequiredMixin, DeleteView):
    """删除学生"""
    role_required = (RoleEnum.ROOT.value, )
    model = Student
    template_name = "students/student_delete.html"
    context_object_name = "student"

    def get_success_url(self):
        messages.success(self.request, "删除学生成功")
        return reverse_lazy("students:students")


class StudentExcelImportView(RoleRequiredMixin, View):
    """学生excel导入视图"""
    role_required = (RoleEnum.ROOT.value, RoleEnum.ACADEMY.value, RoleEnum.SCHOOL.value)
    def post(self, request):
        form = StudentExcelForm(request.POST, request.FILES) # 获取提交后的表单
        fail_list = [] # 失败的学生名单
        success_count = 0 # 成功数
        fail_count = 0 # 失败数
        student_instance_list = [] # 学生实例列表
        if form.is_valid(): # 表单校验通过
            file_obj = request.FILES['excel_file'].read()
            try:
                workbook = xlrd.open_workbook(file_contents=file_obj) # 使用xlrd打开excel文件
                table = workbook.sheets()[0] # 获取第一个工作薄
                nrows = table.nrows # 获取总行数

            except Exception as e:  # 文件内容有误
                return JsonResponse({"status": "fail", "reason": "文件导入失败，请重新刷新页面导入"})

            # 检查文件是否合规
            is_check, check_message = self.check_excel_file(table, nrows)
            if not is_check:
                # 没有通过文件校验，返回错误信息
                return JsonResponse({"status": "fail", "reason": check_message})

            for _ in range(1, nrows): # 从第二行开始导入数据
                row = table.row_values(_) # 获取一条记录
                single_row_check, single_row_message = self.check_single_row(row)
                if not single_row_check:
                    # 行校验不通过，则添加到失败名单
                    return JsonResponse({"status": "fail", "reason": single_row_message})

                is_exist = Student.objects.filter(pk=row[0])
                is_exist_count = is_exist.count()
                if is_exist_count > 0:
                    # 学生数据重复，记录下来
                    fail_count += 1
                    fail_list.append(is_exist[0].uid + "-" + is_exist[0].name)
                else:
                    student = self.build_student(row)
                    student_instance_list.append(student)

            # 保存学生实例到数据库中
            for obj in student_instance_list:
                try:
                    obj.save()
                except Exception as already_exist:
                    return JsonResponse({"status": "fail", "reason": "表格中有学号重复，请在excel中进行学号数据筛选，修改无误后再导入"})
                success_count += 1

            # 写入日志中
            Log.objects.create(
                user=self.request.user,
                content=f"一共导入了{nrows - 1}条学生记录，{success_count}条成功，{fail_count}条失败\n失败的名单如下：{'、'.join(fail_list)}"
            )
            return JsonResponse({"status": "ok", "data": {
                "success_count": success_count,
                "fail_count": fail_count,
                "fail_list": fail_list
            }})

        else: # 文件格式错误
            return JsonResponse({"status": "fail", "reason": "导入的文件必须为xls或xlsx格式！"})

    def check_excel_file(self, table, nrows):
        """
        检查excel文件是否合规
        :param table: excel文件
        :param nrows: 总行数
        :return: boolean
        """
        if nrows <= 1:
            # 行小于等于1，直接报错
            return (False, "excel表格没有填写内容！请重新填写")

        first_row = table.row_values(0)
        if first_row[0] == "学号" and first_row[1] == "姓名" and first_row[2] == "学院" \
            and first_row[3] == "年级" and first_row[4] == "班级" and first_row[5] == "总学时" \
            and first_row[6] == "文体素质学时" and first_row[7] == "法律素养学时" and first_row[8] == "身心素质学时" \
            and first_row[9] == "创新创业素质学时" and first_row[10] == "思想品德素质学时":
            return (True, "ok")
        else:
            return (False, "文件格式错误，请下载模板填写！")

    def check_single_row(self, row):
        """
        检查导入表格的每一行是否符合规范
        :param row: 行
        :return: boolean
        """
        try:
            uid = row[0]
            name = row[1]
        except Exception:
            return (False, "请检查数据是否填写完整！")

        if uid == "":
            return (False, "请仔细检查文件内容！学号不能为空")

        # if str(uid).__contains__("."):
        #     return (False, "学号包含小数点！请手动将表格中的学号改为文本型\n例如将201606126666.0修改为201606126666")
        # if str(uid).__len__() != 12:
        #     # 学号必须为12位
        #     return (False, "请仔细检查文件内容！学号必须为12位，至少有一名学生的学号错误")

        if name == "":
            return (False, "请仔细检查文件内容！学生姓名不能为空")

        try:
            academy = row[2]
            grade = row[3]
            clazz = row[4]
            credit = float(row[5])
            wt_credit = float(row[6])
            fl_credit = float(row[7])
            xl_credit = float(row[8])
            cxcy_credit = float(row[9])
            sxdd_credit = float(row[10])
        except Exception:
            return (False, "请仔细检查文件的错误！")

        if academy == "" or grade == "" or clazz == "":
            return (False, "请仔细检查文件的错误！学院或年级或班级不能为空")

        # if academy != self.request.user.academy:
        #     return (False, "只允许导入" + self.request.user.academy + "的学生信息，其他学院无权限导入")

        # if grade != self.request.user.grade:
        #     return (False, "只允许导入" + self.request.user.academy + self.request.user.grade + "的学生信息，其他年级无权限导入")

        if credit >=0 and wt_credit >=0 and fl_credit >= 0 \
            and xl_credit >=0 and cxcy_credit >=0 and sxdd_credit >= 0:
            return (True, "")
        else:
            return (False, "学时数不能小于0！")

    def build_student(self, row):
        """创建学生的实例"""
        if row[0].__contains__("."):
            row[0] = row[0].split(".")[0]
        return Student(
            uid=row[0], name=row[1], academy=row[2],
            grade=row[3], clazz=row[4], credit=float(row[5]),
            wt_credit=float(row[6]), fl_credit=float(row[7]), xl_credit=float(row[8]),
            cxcy_credit=float(row[9]), sxdd_credit=float(row[10])
        )  # 创建一个学生实例


class StudentExcelExportView(RoleRequiredMixin, View):
    """学生excel导出视图"""
    role_required = (RoleEnum.ACADEMY.value, RoleEnum.ROOT.value)
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
        sheet.write(0, 6, '文体素质学时')
        sheet.write(0, 7, '法律素养学时')
        sheet.write(0, 8, '身心素质学时')
        sheet.write(0, 9, '创新创业素质学时')
        sheet.write(0, 10, '思想品德素质学时')

        students = Student.objects.all()

        if self.request.user.role == RoleEnum.ACADEMY.value:
            students = students.filter(academy=self.request.user.academy,
                                       grade=self.request.user.grade)

        # 写数据
        row = 1
        for student in students: # 单条写入学生数据
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
            return success_response
        except Exception:
            return fail_response


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
        except Exception as e:
            print(e)
            return fail_response
        return success_response


class StudentCreditApplyListView(RoleRequiredMixin, PaginatorListView):
    """学时补录申请列表页
    """
    role_required = (RoleEnum.STUDENT.value, RoleEnum.ACADEMY.value, RoleEnum.SCHOOL.value, RoleEnum.ORG.value)
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
    """
    role_required = (RoleEnum.STUDENT.value, RoleEnum.ACADEMY.value, RoleEnum.SCHOOL.value, RoleEnum.ORG.value)
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
    role_required = (RoleEnum.STUDENT.value, RoleEnum.ACADEMY.value, RoleEnum.SCHOOL.value, RoleEnum.ORG.value)
    def post(self, request):
        form = StudentExcelForm(request.POST, request.FILES) # 获取提交后的表单
        if form.is_valid(): # 表单校验通过
            to_id = request.POST.get("to_id")
            credit_verify_instance_list = [] # 学时补录记录列表
            try:
                to = User.objects.get(pk=to_id)
            except User.DoesNotExist:# 如果查询不到审核者，直接报错
                if request.user.role == RoleEnum.ACADEMY.value or request.user.role == RoleEnum.SCHOOL.value or \
                    request.user.role == RoleEnum.ORG.value:
                    to = request.user
                else:
                    return JsonResponse({"status": "fail", "reason": "请选择审核者"})

            try:
                workbook = xlrd.open_workbook(file_contents=request.FILES['excel_file'].read()) # 使用xlrd打开excel文件
                table = workbook.sheets()[0] # 获取第一个工作薄
                nrows = table.nrows # 获取总行数
            except Exception:
                return JsonResponse({"status": "fail", "reason": "文件导入失败，请重新上传"})

            # 检查文件是否合规
            is_check, check_message = self.check_excel_file(table, nrows)
            if not is_check:
                # 没有通过文件校验，返回错误信息
                return JsonResponse({"status": "fail", "reason": check_message})

            for _ in range(2, nrows): # 从第3行开始导入数据
                row = table.row_values(_) # 获取一条记录

                single_row_check, single_row_message = self.check_single_row(row)
                if not single_row_check:
                    # 行校验不通过，则添加到失败名单
                    return JsonResponse({"status": "fail", "reason": single_row_message})


                obj = self.build_student(row, to, request.user) # 获取补录学时实例
                credit_verify_instance_list.append(obj)

            for credit_verify_instance in credit_verify_instance_list:
                if credit_verify_instance.to == credit_verify_instance.user: # 审核者和申请者相同,增加学时
                    credit_verify_instance.verify = True
                    with transaction.atomic():
                        if not add_credit(CREDIT_TYPE, credit_verify_instance.uid, credit_verify_instance.credit_type, credit_verify_instance.credit):
                            return JsonResponse({"status": "fail", "reason": "学时类别填写错误！可选项为：思想道德素质、创新创业素质、身心素质、文体素质、法律素养"})
                        if not add_student_activity(credit_verify_instance.uid, credit_verify_instance.join_type,
                                                    activity_name=credit_verify_instance.activity_name,
                                                    credit=credit_verify_instance.credit,
                                                    credit_type=credit_verify_instance.credit_type):
                            return JsonResponse({"status": "fail", "reason": "学生活动关联失败"})
                        credit_verify_instance.save()
            # 写入日志中
            Log.objects.create(
                user=self.request.user,
                content=f"导入了{request.FILES.get('excel_file')}表格，共有{nrows - 2}条补录数据，详情内容如下：\n{'，    '.join([o.name + '的' + o.credit_type + '增加了' + str(o.credit) + '个学时' for o in credit_verify_instance_list])}"
            )
            return success_response

        else: # 文件格式错误
            return JsonResponse({"status": "fail", "reason": "必须为xls或xlsx格式！"})

    def check_excel_file(self, table, nrows):
        """
        检查excel文件是否合规
        :param table: excel文件
        :param nrows: 总行数
        :return: boolean
        """
        if nrows <= 2:
            # 行小于等于2，直接报错
            return (False, "excel表格没有填写内容！请重新填写")

        first_row = table.row_values(1)
        if first_row[0] == "活动名称" and first_row[1] == "主办方" and first_row[2] == "姓名" \
            and first_row[3] == "学号" and first_row[4] == "学院" and first_row[5] == "班级" \
            and first_row[6] == "参加类型" and first_row[7] == "获奖情况" and first_row[8] == "认定项目" \
            and first_row[9] == "认定活动时" and first_row[10] == "填报人及联系方式" and first_row[11] == "审核人"\
            and first_row[12] == "备注":
            return (True, "ok")
        else:
            return (False, "文件格式错误，请下载模板填写！")

    def check_single_row(self, row):
        """
        检查导入表格的每一行是否符合规范
        :param row: 行
        :param to: 审核者
        :param user: 当前用户
        :return: boolean
        """
        try:
            activity_name = row[0]
            sponsor = row[1]
            name = row[2]
            uid = row[3]
            academy = row[4]
            clazz = row[5]
            join_type = row[6]
            award = row[7]
            credit_type = row[8]
            credit = row[9]
            contact = row[10]
            to_name = row[11]
            # year = row[13]
        except Exception:
            return (False, "请检查数据是否填写完整！本次操作取消")

        uid = str(uid)

        if uid == "":
            return (False, "表格中的学号不能为空，本次操作取消")

        if uid.__contains__('.'):
            uid = uid.split('.')[0]


        if Student.objects.filter(uid=uid).count() < 1:
            # 学生不存在，不能进行导入
            return (False, f'学号：{uid}，姓名：{row[2]}在系统中不存在，请仔细检查表格是否填写错误！本次操作取消')


        if name == "":
            return (False, "姓名不能为空，本次操作取消")
        if sponsor == "":
            return (False, "主办方不能为空，本次操作取消")
        if clazz == "":
            return (False, "班级不能为空，本次操作取消")
        if academy == "":
            return (False, "学院不能为空，本次操作取消")
        if activity_name == "":
            return (False, "活动名不能为空，本次操作取消")
        if credit_type == "":
            return (False, "学时类别不能为空，本次操作取消")
        if credit == "":
            return (False, "认定活动时不能为空，本次操作取消")
        if contact == "":
            return (False, "联系人不能为空，本次操作取消")
        # if year == "":
        #     return (False, "所属年度不能为空，本次操作取消")

        # if Academy.objects.filter(name=academy).count() < 1:
        #     return (False, f"学院输入错误，系统中不存在{academy}，请纠正！本次操作取消")

        if StudentCreditVerify.objects.filter(activity_name=activity_name, uid=uid, credit_type=credit_type).count() >= 1:
            # 补录活动重复了，不允许导入
            return (False, f'学号：{uid}，姓名：{name}在系统已经有{activity_name}活动的参加记录了，请不要重复导入。建议前往学生的详情页仔细核对')
        try:
            credit = float(row[9])
        except Exception:
            return (False, "认定活动时填写错误！填写的内容需要为数字！请仔细检查表格")

        if credit <= 0:
            return (False, "认定活动时不能小于0！本次操作取消")

        if credit >= 10:
            return (False, "认定活动时不能大于10！本次操作取消")

        if not join_type.strip() in ['参加者', '观众', '工作人员']:
            return (False, "表格中的参加类型必须为 参加者/观众/工作人员其中之一，本次操作取消")

        # 验证所属年度
        # if not "-" in year:
        #     return (False, "所属年度格式为XXXX-XXXX学年，请仔细核对表格的错误格式，本次操作取消")

        return (True, "")


    def build_student(self, row, to, user):
        """创建学生的实例"""
        uid = str(row[3]).strip()
        if uid.__contains__('.'):
            uid = uid.split('.')[0]


        activity_name = str(row[0]).strip()
        sponsor = str(row[1]).strip()
        name = str(row[2]).strip()
        academy = str(row[4]).strip()
        clazz = str(row[5]).strip()
        join_type = str(row[6]).strip()
        award = str(row[7]).strip()
        credit_type = str(row[8]).strip()
        contact = str(row[10]).strip()
        try:
            year = str(row[13]).strip()
        except Exception:
            year = ''

        return StudentCreditVerify(
            activity_name=activity_name, sponsor=sponsor, name=name,
            uid=uid, academy=academy, clazz=clazz,
            join_type=join_type, award=award, credit_type=credit_type,
            credit=row[9], contact=contact, to_name=row[11],
            to=to, user=user, year=year
        )


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
            return fail_response
        return success_response



class StudentCreditApplyManuallyCreateView(RoleRequiredMixin, CreateView):
    """老师手动补录学时"""
    role_required = (RoleEnum.ACADEMY.value, RoleEnum.SCHOOL.value, RoleEnum.ORG.value)
    model = Student
    template_name = "students/student_credit_apply_create_autopass.html"
    form_class = CreditApplyManuallyCreateView

    def form_valid(self, form):
        # 添加日志

        form.instance.user = self.request.user
        form.instance.status = 3
        form.instance.student = Student.objects.get(pk=form.cleaned_data['uid'])

        try:
            StudentCreditVerify.objects.create(
                activity_name=form.instance.activity_name, sponsor=form.cleaned_data['sponsor'], name=form.instance.student_name,
                uid=form.cleaned_data['uid'], academy=form.instance.academy, clazz=form.instance.clazz,
                join_type=form.instance.join_type, award=form.cleaned_data['award'], credit_type=form.instance.credit_type,
                credit=form.instance.credit, contact=form.cleaned_data['contact'], to_name=form.cleaned_data['to_name'],
                to=self.request.user, user=self.request.user, verify=True, year=form.cleaned_data['year']
            )
        except Exception as e:
            return super().form_invalid(form)

        Log.objects.create(
            user=self.request.user,
            content=f"补录了{form.instance.activity_name}活动，学生{form.instance.student_name}的{form.instance.credit_type}增加{form.instance.credit}学时"
        )
        if not add_credit(CREDIT_TYPE, form.cleaned_data['uid'], form.instance.credit_type, form.instance.credit):
            return super().form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "添加补录数据成功")
        return reverse_lazy("students:student_credit_confirm")


class StudentCreditWithdrawView(RoleRequiredMixin, View):
    """撤回审核通过的补录记录"""
    role_required = (RoleEnum.ACADEMY.value, RoleEnum.SCHOOL.value, RoleEnum.ORG.value)
    def post(self, request):
        content_list = []  # 日志内容
        try:
            pks = json.loads(request.POST.get("pks"))

            for pk in pks:
                obj = StudentCreditVerify.objects.get(pk=pk)
                if not minus_credit(CREDIT_TYPE, obj.uid, obj.credit_type, obj.credit): # 减少学时
                    return JsonResponse({"status": "fail", "reason": f'{obj.uid + ":" + obj.name}撤回失败'})
                if not remove_student_activity(obj.uid, obj.join_type,
                                        activity_name=obj.activity_name,
                                        credit=obj.credit,
                                        credit_type=obj.credit_type):  # 删除学生与活动的关联
                    return JsonResponse({"status": "fail", "reason": f'{obj.uid + ":" + obj.name}撤回失败'})

                obj.delete() # 删除审核记录
                content_list.append(f'{obj.name}撤回{obj.credit_type}的{obj.credit}个学时')
        except Exception as e:
            return fail_response

        Log.objects.create(
            user=self.request.user,
            content=f"撤回了{len(pks)}条补录学时数据，详情内容如下：{'，    '.join(content_list)}"
        )

        return success_response


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
            return fail_response
        return success_response


class StudentCreditVerifyListView(RoleRequiredMixin, PaginatorListView):
    """学生组织审核学时列表页
    权限：院级和学生组织
    """
    role_required = (RoleEnum.ACADEMY.value, RoleEnum.SCHOOL.value, RoleEnum.ORG.value)
    paginate_by = 100
    context_object_name = "students"
    template_name = "students/student_credit_verify_list.html"

    def get_queryset(self):
        return self.request.user.waiting_to_verify_credits.filter(verify=False)


class StudentCreditVerifyEditView(RoleRequiredMixin, UpdateView):
    """修改审核通过的学时补录记录
    """
    role_required = (RoleEnum.ACADEMY.value, RoleEnum.SCHOOL.value, RoleEnum.ORG.value)
    model = StudentCreditVerify
    context_object_name = "record"
    template_name = "students/student_credit_verify_update.html"
    form_class = CreditVerifyUpdateForm

    def form_valid(self, form):
        # 添加日志
        Log.objects.create(
            user=self.request.user,
            content=f"修改了补录记录<活动：{form.instance.name}>"
        )
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "修改成功")
        return reverse_lazy("students:student_credit_confirm")


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
            return fail_response
        return success_response
