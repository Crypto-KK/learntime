from django.db import models
from django.db.models import DateTimeField

from learntime.activity.models import Activity
from learntime.student.models import Student


class StudentActivity(models.Model):

    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING,
                                verbose_name="学生")
    activity = models.ForeignKey(Activity, on_delete=models.DO_NOTHING,
                                 verbose_name="活动")
    create_time = DateTimeField(db_index=True, auto_now_add=True,
                                verbose_name='创建时间')
    join_type = models.CharField(max_length=255, verbose_name="参与类型")


    class Meta:
        verbose_name = "学生活动表"
        verbose_name_plural = verbose_name
        db_table = "student_activities"
