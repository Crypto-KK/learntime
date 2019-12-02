学时通后台管理系统
=========

学时通后台管理系统


项目运行
^^^^^^^^^^^^^^^^^^^^^

* 版本要求：Python3.6及以上版本、Django2.2.0以上版本
* 依赖说明：使用Pipenv虚拟环境，使用如下命令安装依赖::

    $ pipenv install --skip-lock

* 使用以下命令创建 **空数据表**::

    $ python manage.py migrate

* 使用以下命令创建 **超级管理员账号**::

    $ python manage.py createsuperuser

* 使用以下命令在开发机中运行项目::

    $ python manage.py runserver 0.0.0.0:8000

* 如需编辑项目中的敏感配置，请在项目目录下编辑.env文件

类型检查
^^^^^^^^^^^

使用mypy运行如下命令:

::

  $ mypy learntime


部署
----------

本项目使用Nginx+uWSGI+supervisor部署在CentOS系统中




