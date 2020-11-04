import logging

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from generate_student import generate_student
from learntime.statistic.models import CreditStat
from learntime.student.models import Student, StudentCreditVerify


class Command(BaseCommand):
    """python manage.py runstat --test | record"""
    logger = logging.getLogger("django")
    def __init__(self):
        super().__init__()
        self.User = get_user_model()

    def handle(self, *args, **options):
        if options.get('test'):
            self.test()
        if options.get("record"):
            self.record()
        if options.get("generate"):
            self.generate()
        if options.get("check"):
            self.auto_check()

        #self.stdout.write(self.style.SUCCESS('adsf'))
    def add_arguments(self, parser):
        parser.add_argument('--test', help="测试定时任务是否启动", action='store_true')
        parser.add_argument('--record', help="启动按月学时统计任务", action='store_true')
        parser.add_argument('--generate', help="启动批量生成学生账号任务", action='store_true')
        parser.add_argument('--checkscore', help="启动修正学时任务", action='store_true')

    def test(self):
        self.logger.info("test crontab")

    def record(self):
        from datetime import date, datetime
        students = Student.objects.all()
        for student in students:
            try:
                credit_stat_last_month = CreditStat.objects.filter(uid=student.uid)[0]
            except Exception:
                # 上个月没有该学生的记录
                credit_stat_last_month = None

            diff = student.credit - getattr(credit_stat_last_month, 'credit', student.credit)
            diff_cxcy = student.cxcy_credit - getattr(credit_stat_last_month, 'cxcy_credit', student.cxcy_credit)
            diff_sxdd = student.sxdd_credit - getattr(credit_stat_last_month, 'sxdd_credit', student.sxdd_credit)
            diff_fl = student.fl_credit - getattr(credit_stat_last_month, 'fl_credit', student.fl_credit)
            diff_wt = student.wt_credit - getattr(credit_stat_last_month, 'wt_credit', student.wt_credit)
            diff_xl = student.xl_credit - getattr(credit_stat_last_month, 'xl_credit', student.xl_credit)

            CreditStat.objects.create(
                uid=student.uid,
                name=student.name,
                grade=student.grade,
                clazz=student.clazz,
                academy=student.academy,
                credit=student.credit,
                sxdd_credit=student.sxdd_credit,
                cxcy_credit=student.cxcy_credit,
                fl_credit=student.fl_credit,
                wt_credit=student.wt_credit,
                xl_credit=student.xl_credit,
                record_time=date.today(),
                diff=diff,
                diff_cxcy=diff_cxcy,
                diff_sxdd=diff_sxdd,
                diff_fl=diff_fl,
                diff_xl=diff_xl,
                diff_wt=diff_wt
            )
        self.logger.info(f"统计学时于{datetime.now()}完成")
        self.stdout.write(self.style.SUCCESS('统计学时完成'))

    def generate(self):
        self.logger.info("开始批量生成学生账号")
        self.stdout.write(self.style.SUCCESS('开始批量生成学生账号'))
        result = generate_student()
        self.stdout.write(self.style.SUCCESS(result))
        self.logger.info(result)


    def auto_check(self):
        self.logger.info("启动学时修正")
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
