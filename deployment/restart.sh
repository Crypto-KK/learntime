#!/bin/bash

cd /root/learntime/&&
pkill -f uwsgi -9&&
rm -f w1*.log&&
rm -f w1.pid&&
rm -f worker*.log&&
rm -f worker.pid&&
echo "清除celery文件成功"
pkill -f celery -9&&
echo "关闭uwsgi和celery服务成功"
echo "正在重启项目，请稍后"
/usr/local/python3/bin/uwsgi -d -i deployment/uwsgi.ini&&
#/usr/local/python3/bin/celery -A config.celery_app worker -l info
/usr/local/python3/bin/celery multi start w1 -A config.celery_app worker -l info
echo "启动项目成功"
