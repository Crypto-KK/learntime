from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from learntime.operation.models import StudentActivity, Comment
from learntime.utils.helpers import add_credit

@receiver(post_save, sender=StudentActivity)
def sign_out_activity(sender, instance=None, created=False, **kwargs):
    """
    签退活动，增加学时
    """
    if not created and instance.status != 3:
        # 当status状态更新为签退成功时，增加学时
        print("qiandui")
        credit = instance.credit
        credit_type = instance.credit_type
        # 增加学时
        add_credit(settings.CREDIT_TYPE, instance.student_id, credit_type, credit)


