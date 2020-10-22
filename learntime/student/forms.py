from django import forms
from django.contrib.auth import get_user_model

from learntime.student.models import Student, StudentFile, StudentCreditVerify
from learntime.users.models import Academy, Grade
from learntime.operation.models import StudentActivity


class StudentCreateForm(forms.ModelForm):
    uid = forms.CharField(label="学号")
    academy = forms.ModelChoiceField(label="学院", queryset=Academy.objects.all())
    grade = forms.ModelChoiceField(label="年级", queryset=Grade.objects.all())
    class Meta:
        exclude = ('credit', )
        model = Student


class StudentEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['uid'].widget.attrs['readonly'] = True
    uid = forms.CharField(label="学号", help_text="无法修改学号")
    academy = forms.ModelChoiceField(queryset=Academy.objects.all(), help_text="选择学院")
    grade = forms.ModelChoiceField(queryset=Grade.objects.all(), help_text="选择年级")

    class Meta:
        fields = ("uid", "name", "grade", "academy", "clazz")
        model = Student


class StudentExcelForm(forms.ModelForm):
    """导入学生excel表单"""
    class Meta:
        fields = "__all__"
        model = StudentFile

    def clean_excel_file(self):
        excel_file = self.cleaned_data['excel_file']
        if excel_file.name.split('.')[-1] not in ("xls", "xlsx", ):
            raise forms.ValidationError("后缀必须为xls或xlsx!")
        return excel_file


class StudentCreditCreateForm(forms.ModelForm):
    """补录数据表单"""
    to = forms.ModelChoiceField(queryset=get_user_model().objects.filter(role=3),
                                help_text='选择审核者')
    class Meta:
        exclude = ('verify', 'user')
        model = StudentCreditVerify

    def clean_uid(self):
        uid = self.cleaned_data['uid']
        try:
            Student.objects.get(pk=uid)
        except Student.DoesNotExist:
            raise forms.ValidationError("该学号不存在")
        return uid

    def clean(self):
        uid = self.cleaned_data.get("uid")
        name = self.cleaned_data.get("name")
        try:
            Student.objects.filter(uid=uid, name=name)[0]
        except IndexError:
            raise forms.ValidationError("学号和姓名不匹配")
        return super().clean()


class CreditApplyManuallyCreateView(forms.ModelForm):
    """手动填写学时补录的表单"""
    uid = forms.CharField(label="学号", required=True)
    name = forms.CharField(label="姓名", required=True)
    academy = forms.ModelChoiceField(empty_label="请选择学院", queryset=Academy.objects.all(), label="学院")
    grade = forms.ModelChoiceField(empty_label="请选择年级", queryset=Grade.objects.all(), label="学院")
    clazz = forms.CharField(label="班级", required=True)
    sponsor = forms.CharField(label="主办方", required=True)
    activity_name = forms.CharField(label="活动名称", required=True)
    award = forms.CharField(label="获奖情况", required=True, help_text="若没有请填写无")
    year = forms.CharField(label="所属年度", required=False, help_text="例如：2020-2021学年")

    join_type = forms.ChoiceField(
        choices=(
            ('参加者', '参加者'),
            ('观众', '观众'),
            ('工作人员', '工作人员')
        ),
        label="参与类型"
    )

    credit_type = forms.ChoiceField(
        choices=(
            ('身心素质', '身心素质'),
            ('法律素养', '法律素养'),
            ('文体素质', '文体素质'),
            ('思想品德素质', '思想品德素质'),
            ('创新创业素质', '创新创业素质')
        ),
        label="学时类型"
    )

    credit = forms.FloatField(max_value=100, min_value=0.25, label="认定学时")

    contact = forms.CharField(label="填表人及联系方式", required=True)
    to_name = forms.CharField(label="审核人", required=True)

    def clean_uid(self):
        uid = self.cleaned_data['uid']
        try:
            Student.objects.get(pk=uid)
        except Student.DoesNotExist:
            raise forms.ValidationError("该学号不存在")
        return uid

    class Meta:
        model = StudentCreditVerify
        fields = ('uid', 'name', 'academy', 'grade', 'clazz',
                  'activity_name', 'join_type', 'credit_type', 'credit',
                  "sponsor", "award", "year", "contact", "to_name")


class CreditVerifyUpdateForm(forms.ModelForm):
    """学时补录成功后进行修改"""

    class Meta:
        model = StudentCreditVerify
        exclude = ('verify', 'to', 'user', 'uid', 'name', 'academy', 'clazz')

    def clean_credit_type(self):
        s = self.cleaned_data['credit_type']
        if s not in ['思想品德素质', '创新创业素质', '法律素养', '身心素质', '文体素质']:
            raise forms.ValidationError("学时类别必须填写思想品德素质、创新创业素质、法律素养、身心素质、文体素质")
        return s

    def clean_credit(self):
        s = self.cleaned_data['credit']
        if s <= 0 or s > 10:
            raise forms.ValidationError("认定活动时必须大于0且小于10")
        return s
