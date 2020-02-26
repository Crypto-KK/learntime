import logging

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """python manage.py runstat --test"""
    logger = logging.getLogger("django")
    def __init__(self):
        super().__init__()
        self.User = get_user_model()

    def handle(self, *args, **options):

        if options.get('test'):
            self.test()

        #self.stdout.write(self.style.SUCCESS('adsf'))
    def add_arguments(self, parser):
        parser.add_argument('--test', help="测试定时任务是否启动", action='store_true')

    def test(self):
        print("test crontab")
        self.logger.info("test crontab")
