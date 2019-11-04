from django import forms

from learntime.student.models import Student


class StudentForm(forms.ModelForm):
    uid = forms.CharField(help_text="学号")
    class Meta:
        exclude = ('password', )
        model = Student
