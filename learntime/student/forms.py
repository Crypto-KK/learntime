from django import forms
from django.contrib.auth import get_user_model

from learntime.student.models import Student, StudentFile, StudentCreditVerify
from learntime.users.models import Academy, Grade


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
        if excel_file.name.split('.')[1] not in ("xls", "xlsx", ):
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
