from django import forms

from learntime.activity.models import Activity


class ActivityForm(forms.ModelForm):
    class Meta:
        exclude = ("user", "uid", "is_verify")
        model = Activity
