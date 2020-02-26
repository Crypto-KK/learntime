import logging

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from learntime.statistic.models import CreditStat
from learntime.student.models import Student


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

        #self.stdout.write(self.style.SUCCESS('adsf'))
    def add_arguments(self, parser):
        parser.add_argument('--test', help="测试定时任务是否启动", action='store_true')
        parser.add_argument('--record', help="启动按月学时统计任务", action='store_true')

    def test(self):
        self.logger.info("test crontab")

    def record(self):
        from datetime import date, datetime
        students = Student.objects.all()
        for student in students:
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
                record_time=date.today()
            )
        self.logger.info(f"统计学时于{datetime.now()}完成")
        self.stdout.write(self.style.SUCCESS('统计学时完成'))
