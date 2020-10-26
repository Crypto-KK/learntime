"""
自动修正学生的学时
"""
import django

django.setup()

from learntime.student.models import Student, StudentCreditVerify


for student in Student.objects.all():
    uid = student.uid
    records = StudentCreditVerify.objects.filter(uid=uid, verify=True, is_fail=False)
    credit = 0
    sxdd_credit = 0
    cxcy_credit = 0
    xl_credit = 0
    fl_credit = 0
    wt_credit = 0
    for record in records:
        if record.credit_type == "创新创业素质":
            cxcy_credit += record.credit
        elif record.credit_type == "思想品德素质":
            sxdd_credit += record.credit
        elif record.credit_type == "文体素质":
            wt_credit += record.credit
        elif record.credit_type == "法律素养":
            fl_credit += record.credit
        elif record.credit_type == "身心素质":
            sxdd_credit += record.credit
    credit = sxdd_credit + cxcy_credit + xl_credit + fl_credit + wt_credit
    if student.credit == credit:
        print(student.name + "无需修正")
    else:
        student.credit = credit
        student.sxdd_credit = sxdd_credit
        student.cxcy_credit = cxcy_credit
        student.xl_credit = xl_credit
        student.fl_credit = fl_credit
        student.wt_credit = wt_credit
        student.save()
        print(student.name + "修正成功，修正后的学时为：" + str(credit))
