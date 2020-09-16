FROM python:3.7
MAINTAINER liyuankun 705555262@qq.com
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /learntime
WORKDIR /learntime

ADD ../.. /learntime/
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple uwsgi
