#!/bin/bash
python manage.py collectstatic --noinput&&
#python manage.py makemigrations&&
#python manage.py migrate&&
#python manage.py createsuperuser&&
#gunicorn config.wsgi:application -c gunicorn.conf
#celery multi start w1 -A config.celery_app worker -l info&&
celery multi start w1 -A config.celery_app worker -l info&&
uwsgi -i ./uwsgi.ini
