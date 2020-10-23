# 学时通后台管理系统

## 本地运行
* 版本要求：Python3.7及以上版本、Django2.2.0以上版本
* 依赖说明：使用虚拟环境，使用如下命令安装依赖:
```
    pip install -r requirements.txt
```
* 启动前检查：确保`.env`文件在项目目录中，并且在该文件中配置数据库的连接地址以及redis地址
* 运行项目，使用一下命令：
```
    python3 manage.py runserver 0.0.0.0:8000
```

## 部署
请使用CentOS7.0以上版本部署

### 1.安装系统依赖
```
(root)$ yum -y update
(root)$ yum install -y install python-devel zlib-devel mysql-devel libffi-devel openssl-devel bzip2-devel ncurses-devel sqlite-devel readline-devel tk-devel java wget gcc make tmux
```

### 2.安装Python3.7.4版本
```
(root)$ wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz

#编译python
(root)$ tar -zxvf Python-3.7.4.tgz
(root)$ cd Python-3.7.4
(root)$ ./configure --prefix=/usr/local/python3 --enable-optimizations
(root)$ make&&make install

#添加软连接
(root)$ ln -s /usr/local/python3/bin/python3 /usr/bin/python3
(root)$ ln -s /usr/local/python3/bin/pip3 /usr/bin/pip3
```
注意：加上`--enable-optimizations`后make的速度非常慢，但是执行Python代码时会有10%-20%的性能提升。


### 3. 安装git/redis/nginx
```
(root)$ yum -y install git redis nginx supervisor
```

### 4. 设置开机启动
保证重启后依然能运行
```
(root)$ systemctl enable redis nginx supervisord
```


### 5. 安装项目需要的包
```
(root)$ pip3 install -r requirements.txt
(root)$ pip3 install uwsgi
```

### 6. 使用uwsgi启动项目

先启动celery邮箱服务
```
/usr/local/python3/bin/celery -A config.celery_app worker -l info
```

再使用uwsgi启动django
```
(root)$ uwsgi -d -i deployment/uwsgi.ini
```
关闭uwsgi
```
(root)$ pkill -f uwsgi -9
```

### 7. 使用nginx反向代理

进入项目目录中的deployment/nginx文件夹，将nginx.conf文件拷贝到/etc/nginx/中


## 注意事项
请保证nginx和redis服务在重启后能够自动运行，需要使用`systemctl enable nginx和redis`
