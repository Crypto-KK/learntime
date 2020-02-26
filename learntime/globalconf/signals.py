from django.db.models.signals import post_save
from django.dispatch import receiver

from learntime.globalconf import middleware
from learntime.globalconf.models import Configration


@receiver(post_save, sender=Configration)
def maintenance_change(sender, instance=None, created=False, **kwargs):
    """
    维护状态修改时
    """
    middleware.is_maintenance = instance.is_maintenance
    middleware.maintenance_notice = instance.maintenance_notice
