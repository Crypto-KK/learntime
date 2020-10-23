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
