# Generated by Django 2.2.6 on 2019-11-04 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('uid', models.CharField(editable=False, max_length=255, primary_key=True, serialize=False, verbose_name='学号')),
                ('name', models.CharField(max_length=255, verbose_name='姓名')),
                ('academy', models.CharField(blank=True, max_length=255, null=True, verbose_name='学院')),
                ('info', models.CharField(max_length=255, verbose_name='其他信息')),
                ('credit', models.FloatField(default=0, verbose_name='学时')),
                ('cxcy_credit', models.FloatField(default=0, verbose_name='创新创业学时')),
                ('sxdd_credit', models.FloatField(default=0, verbose_name='思想道德学时')),
                ('fl_credit', models.FloatField(default=0, verbose_name='法律学时')),
                ('wt_credit', models.FloatField(default=0, verbose_name='问题学时')),
                ('xl_credit', models.FloatField(default=0, verbose_name='心理学时')),
            ],
            options={
                'verbose_name': '学生',
                'verbose_name_plural': '学生',
                'db_table': 'student',
            },
        ),
    ]