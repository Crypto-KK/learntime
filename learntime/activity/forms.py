from django import forms

from learntime.activity.models import Activity


class ActivityForm(forms.ModelForm):
    class Meta:
        exclude = ("user", "uid", "is_verify")
        model = Activity

    def clean_credit_type(self):
        # 学时类别选择了 未选择 ，验证失败
        credit_type = self.cleaned_data['credit_type']
        if credit_type == "n":
            raise forms.ValidationError("请选择学时类别")
        return credit_type
