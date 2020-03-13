from django.conf import settings
from django.core.mail import send_mail

from config import celery_app


@celery_app.task()
def send_activity_verify_email(email):
    """异步发送新订单邮件"""
    title = '[学时通] 您有一个新活动等待审核'
    message = '您有一个新活动等待审核，请进入学时通管理系统查看'
    recipient_list = []
    recipient_list.append(email)
    send_mail(title, message=message, from_email=settings.DEFAULT_FROM_EMAIL,
              recipient_list=recipient_list)
