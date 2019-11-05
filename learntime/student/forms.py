from django import forms

from learntime.student.models import Student, StudentFile


class StudentForm(forms.ModelForm):
    uid = forms.CharField(help_text="学号")
    class Meta:
        exclude = ('password', )
        model = Student


class StudentExcelForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = StudentFile

    def clean_excel_file(self):
        excel_file = self.cleaned_data['excel_file']
        if excel_file.name.split('.')[1] not in ("xls", "xlsx", ):
            raise forms.ValidationError("后缀必须为xls或xlsx!")
        return excel_file

