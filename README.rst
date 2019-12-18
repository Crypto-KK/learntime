学时通后台管理系统
=========

学时通后台管理系统


项目运行
^^^^^^^^^^^^^^^^^^^^^

* 版本要求：Python3.6及以上版本、Django2.2.0以上版本
* 依赖说明：使用虚拟环境，使用如下命令安装依赖::

    $ pip install -r requirements.txt

* 使用以下命令生成 **数据库迁移文件**::

    $ python manage.py makemigrations

* 使用以下命令创建 **空数据表**::

    $ python manage.py migrate

* 使用以下命令创建 **超级管理员账号**::

    $ python manage.py createsuperuser

* 使用以下命令在开发机中运行项目::

    $ python manage.py runserver 0.0.0.0:8000

* 如需编辑项目中的配置信息，请在项目目录下编辑.env文件


部署
----------

方式1：Nginx+uWSGI+supervisor部署在CentOS系统中
方式2：Docker部署在CentOS系统中（推荐）



