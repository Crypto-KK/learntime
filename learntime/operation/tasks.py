from django.conf import settings
from django.core.mail import send_mail

from config import celery_app


@celery_app.task()
def send_email_to_user(email, title, content):
    """异步发送邮件给用户"""
    recipient_list = []
    recipient_list.append(email)
    send_mail(title, message=content, from_email=settings.DEFAULT_FROM_EMAIL,
              recipient_list=recipient_list)
