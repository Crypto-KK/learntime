from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()


class LoginForm(forms.ModelForm):

    class Meta:
        fields = ['email', 'password']
        model = User
