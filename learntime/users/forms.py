from django.contrib.auth import get_user_model
from django import forms

from learntime.users.models import Academy, Grade

User = get_user_model()


class LoginForm(forms.ModelForm):

    class Meta:
        fields = ['email', 'password']
        model = User


class RegisterForm(forms.ModelForm):

    def clean_email(self):
        email = self.cleaned_data['email']
        is_exists = User.objects.filter(email=email).count()
        if is_exists:
            raise forms.ValidationError("邮箱重复！")
        return email

    academy = forms.CharField()
    grade =forms.CharField()

    class Meta:
        fields = ['username', 'name', 'email', 'password', 'identity']
        model = User


class UserForm(forms.ModelForm):
    academy = forms.ModelChoiceField(queryset=Academy.objects.all(),
                                     )
    grade = forms.ModelChoiceField(queryset=Grade.objects.all())
    class Meta:
        fields = ['name', "email", "academy", "grade", "klass"]
        model = User
