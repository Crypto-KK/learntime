"""
自动生成学生账号和密码
"""
import django
import hashlib
django.setup()

from learntime.student.models import SimpleStudent, Student

def gen_md5(src):
    m1 = hashlib.md5()
    m1.update(src)
    return m1.hexdigest()

students = Student.objects.all() # 获取系统中所有学生名单


for student in students[:3]:
    try:
        simple_student = SimpleStudent.objects.create(
            uid=student.uid,
            name=student.name,
            grade=student.grade,
            academy=student.academy,
            clazz=student.clazz,
            credit=student.credit,
            cxcy_credit=student.cxcy_credit,
            sxdd_credit=student.sxdd_credit,
            fl_credit=student.fl_credit,
            wt_credit=student.wt_credit,
            xl_credit=student.xl_credit,
            password=gen_md5(student.uid[6:].encode("utf-8"))
        )
    except Exception as e:
        print(e)
        print(student.uid + '  生成失败')

