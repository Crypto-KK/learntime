from django.dispatch import receiver
from django.db.models.signals import post_save

from learntime.activity.models import Activity
from learntime.operation.models import Log


@receiver(post_save, sender=Activity)
def after_create_activity(sender, instance=None, created=False, **kwargs):
    """发布活动后，创建日志"""
    if created:
        Log.objects.create(
            user=instance.user,
            content=f"发布了活动<{instance.name}>"
        )
    else:
        # 活动审核通过
        if instance.is_verify:
            if not instance.to_school:
                # 院级审核通过

                # 给发布活动者记录日志
                Log.objects.create(
                    user=instance.user,
                    content=f"活动<{instance.name}>审核成功，经办人：{instance.to.name}"
                )
                # 给院级记录日志
                Log.objects.create(
                    user=instance.to,
                    content=f"我批准了活动<{instance.name}>"
                )
            else:
                # 校级审核通过 给发布活动者记录日志
                Log.objects.create(
                    user=instance.user,
                    content=f"活动<{instance.name}>审核成功，经办人：{instance.to_school.name}"
                )
                # 给校级记录日志
                Log.objects.create(
                    user=instance.to_school,
                    content=f"我批准了活动<{instance.name}>"
                )
        else:
            if instance.reason and not instance.is_verifying:
                # 审核不通过
                Log.objects.create(
                    user=instance.user,
                    content=f"活动<{instance.name}>审核失败，原因：{instance.reason}"
                )

                # 给操作者添加日志
                Log.objects.create(
                    user=instance.to or instance.to_school,
                    content=f"我不批准活动<{instance.name}>，原因：{instance.reason}"
                )
            if instance.is_verifying and instance.to_school:
                # 操作了提交给上级按钮 给发布活动者添加日志
                Log.objects.create(
                    user=instance.user,
                    content=f"活动<{instance.name}>已提交给上级审核，经办人：{instance.to}，上级：{instance.to_school}"
                )
                # 给操作者添加日志
                Log.objects.create(
                    user=instance.to,
                    content=f"我提交活动<{instance.name}>给上级审核，上级审核者：{instance.to_school}"
                )

