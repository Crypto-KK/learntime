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


def generate_student():
    students = Student.objects.all() # 获取系统中所有学生名单
    success_count = 0
    fail_count = 0

    for student in students:
        try:
            SimpleStudent.objects.create(
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
            success_count += 1
        except Exception:
            fail_count += 1

    return f"成功：{success_count}个，失败：{fail_count}个"
