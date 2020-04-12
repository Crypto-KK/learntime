from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.forms import ModelForm

from learntime.users.models import Academy, Grade, Institute

User = get_user_model()

class LoginForm(forms.ModelForm):
    # @property
    # def helper(self):
    #     helper = FormHelper()
    #     helper.label_class = 'label-material'
    #     helper.layout = Layout(
    #         Field('email', css_class='input-material'),
    #         Field('password', css_class='input-material')
    #     )
    #     return helper

    class Meta:
        fields = ['email', 'password']
        model = User
        # widgets = {
        #     'email': forms.EmailInput(attrs={'class': 'input-material'}),
        #     'password': forms.PasswordInput(attrs={'class': 'input-material'})
        # }


class RegisterForm(forms.ModelForm):

    def clean_email(self):
        email = self.cleaned_data['email']
        is_exists = User.objects.filter(email=email).count()
        if is_exists:
            raise forms.ValidationError("邮箱重复！")
        return email

    def clean(self):
        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']
        if password2 != password:
            raise forms.ValidationError("两次输入密码不一致")
        return self.cleaned_data

    def clean_organization(self):

        print(self.cleaned_data['organization'])
        return self.cleaned_data['organization']

    academy = forms.CharField()
    grade =forms.CharField()
    password2 = forms.CharField()

    class Meta:
        fields = ['name', 'email', 'password', 'role', 'department', 'organization']
        model = User


class UserForm(forms.ModelForm):
    academy = forms.ModelChoiceField(queryset=Academy.objects.all(),
                                     required=False, help_text="可不填写", label="学院")
    grade = forms.ModelChoiceField(queryset=Grade.objects.all(),
                                   required=False, help_text="可不填写", label="年级")
    class Meta:
        fields = ['name', "email", "academy", "grade", "klass", "role"]
        model = User


class ForgetForm(PasswordResetForm):

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email, is_active=True).count() == 0:
            raise forms.ValidationError("邮箱尚未注册！")
        return email


class InstituteForm(ModelForm):

    class Meta:
        exclude = ('user',)
        model = Institute
