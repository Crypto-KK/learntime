#!/bin/bash

cd /root/learntime/&&
/usr/local/python3/bin/uwsgi -d -i deployment/uwsgi.ini&&
/usr/local/python3/bin/celery -A config.celery_app worker -l info
