from django.conf import settings
from django.core.mail import send_mail

from config import celery_app


@celery_app.task()
def send_user_verify_email(email):
    """异步发送审核通过邮件"""
    title = '[广州商学院学时通] 恭喜您账号审核通过'
    message = '请进入学时通后台管理系统登录，地址：http://39.108.165.160:8000'
    recipient_list = []
    recipient_list.append(email)
    send_mail(title, message=message, from_email=settings.DEFAULT_FROM_EMAIL,
              recipient_list=recipient_list)


@celery_app.task()
def send_code_email(email, code):
    """发送邮箱验证码"""
    title = '[广州商学院学时通] 改绑邮箱'
    message = '您的验证码为：' + code
    recipient_list = []
    recipient_list.append(email)
    send_mail(title, message=message, from_email=settings.DEFAULT_FROM_EMAIL,
              recipient_list=recipient_list)
