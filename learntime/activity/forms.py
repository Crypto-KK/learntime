from django import forms

from learntime.activity.models import Activity


class ActivityForm(forms.ModelForm):
    #academy = forms.ModelChoiceField(label="选择学院", queryset=Academy.objects.all())
    #to = forms.ChoiceField(label="选择审核者")

        #self.fields['to'].choices = ((x.pk, x.name) for )

    class Meta:
        exclude = ("user", "uid", "is_verify", "is_academy_verify",
                   "is_school_verify", "to", "is_verifying", "reason", "to_school",
                   "stop")
        model = Activity


    def clean_credit_type(self):
        # 学时类别选择了 未选择 ，验证失败
        credit_type = self.cleaned_data['credit_type']
        if credit_type == "n":
            raise forms.ValidationError("请选择学时类别")
        return credit_type


    # def clean_file(self):
    #     file = self.cleaned_data['file']
    #     if file.name.split('.')[1] not in ("doc", "docx", ):
    #         raise forms.ValidationError("后缀必须为doc或docx")
    #     return file
