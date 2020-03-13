from django.dispatch import receiver
from django.db.models.signals import post_save

from learntime.student.models import Student, SimpleStudent


@receiver(post_save, sender=Student)
def sync_with_student(sender, instance=None, created=False, **kwargs):
    """student_backend表和student表同步"""
    if not created:
        # only for updated
        student = instance
        simple_student = SimpleStudent.objects.get(pk=student.pk)
        if simple_student:
            simple_student.credit = student.credit
            simple_student.cxcy_credit = student.cxcy_credit
            simple_student.sxdd_credit = student.sxdd_credit
            simple_student.fl_credit = student.fl_credit
            simple_student.wt_credit = student.wt_credit
            simple_student.xl_credit = student.xl_credit
            simple_student.save()
