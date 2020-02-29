from datetime import datetime

from django import forms

from ckeditor.fields import RichTextFormField

from learntime.activity.models import Activity, JOIN_TYPE


class ActivityForm(forms.ModelForm):
    """活动表单，所有字段必须不为null"""
    #academy = forms.ModelChoiceField(label="选择学院", queryset=Academy.objects.all())
    #to = forms.ChoiceField(label="选择审核者")

        #self.fields['to'].choices = ((x.pk, x.name) for )
    logo = forms.ImageField(required=True, label="活动图标", help_text="请务必上传")
    file = forms.FileField(required=False, label="活动策划表", help_text="请上传.doc或.docx后缀的文档，若没有可以不上传")
    sponsor = forms.CharField(required=True, label="主办方", max_length=255)
    credit_type = forms.ChoiceField(choices=Activity.TYPE, label="学时类别", required=True)
    nums = forms.IntegerField(label="名额数量", help_text="若无名额限制，请不要填写该内容", required=False)
    place = forms.CharField(required=True, label="活动地点")
    time = forms.CharField(required=True, label="活动时间")
    deadline = forms.DateTimeField(required=True, label="活动截止日期", help_text="请选择大于现在的日期")
    desc = RichTextFormField(required=True, label="活动描述")
    join_type = forms.ChoiceField(choices=JOIN_TYPE, label="参与身份", required=True)
    score = forms.FloatField(required=True, label="获得学时")


    class Meta:
        exclude = ("user", "uid", "is_verify", "is_academy_verify",
                   "is_school_verify", "to", "is_verifying", "reason", "to_school",
                   "stop", "is_craft")
        model = Activity

    def clean_credit_type(self):
        # 学时类别选择了 未选择 ，验证失败
        credit_type = self.cleaned_data['credit_type']
        if credit_type == "n":
            raise forms.ValidationError("请选择学时类别")
        return credit_type

    def clean_deadline(self):
        # 验证活动截止时间
        deadline = self.cleaned_data.get("deadline")
        if deadline:
            if datetime.now() > deadline:
                raise forms.ValidationError("活动截止时间设置错误")
        return deadline

    def clean(self):
        cd = self.cleaned_data
        desc, score, nums, logo= cd.get("desc"), cd.get("score"), cd.get("nums"), \
                                        cd.get("logo")
        if not desc:
            raise forms.ValidationError("请填写活动描述！")
        if not(score and score > 0):
            raise forms.ValidationError("获得学时不得小于0！")
        if not (nums and nums > 0):
            raise forms.ValidationError("名额数量不得小于0！")
        if not logo:
            raise forms.ValidationError("请上传活动图标！")
        return cd


class ActivityCraftForm(forms.ModelForm):
    """草稿箱表单，活动名称必填！"""
    class Meta:
        exclude = ("user", "uid", "is_verify", "is_academy_verify",
                   "is_school_verify", "to", "is_verifying", "reason", "to_school",
                   "stop", "is_craft")
        model = Activity

    time = forms.CharField(required=False, label="活动时间", help_text="此处可以自行手动填写，或者选择特定的日期")
    logo = forms.ImageField(required=False, label="活动图标", help_text="")
    file = forms.FileField(required=False, label="活动策划表", help_text="请上传.doc或.docx后缀的文档，若没有可以不上传")
    def clean_deadline(self):
        # 验证活动截止时间
        deadline = self.cleaned_data['deadline']
        if deadline:
            if datetime.now() > deadline:
                raise forms.ValidationError("活动截止时间设置错误")
        return deadline

    # def clean_file(self):
    #     file = self.cleaned_data.get("file")
    #     if not (file and file.__str__().split(".")[-1] in ("doc", "docx")):
    #         raise forms.ValidationError("活动策划表必须为.doc或.docx格式！")
    #     return file
    # def clean(self):
    #     print(self.cleaned_data)
    #     return self.cleaned_data
