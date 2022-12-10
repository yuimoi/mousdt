#!/bin/bash

# 安装supervisor
if awk -F= '/^NAME/{print $2}' /etc/os-release | grep -qi 'centos'; then
  yum install epel-release -y
  yum install supervisor -y
  SUPERVISOR_PROJECT_CONFIG_PATH=/etc/supervisord.d/mousdt.ini

elif awk -F= '/^NAME/{print $2}' /etc/os-release | grep -qi 'ubuntu\|debian'; then
  apt-get install supervisor -y
  SUPERVISOR_PROJECT_CONFIG_PATH=/etc/supervisor/conf.d/mousdt.conf
fi

# supervisor开机自启动
systemctl enable supervisord
# supervisor启动
systemctl start supervisord

# 创建mousdt的守护进程配置/etc/supervisor/conf.d/mousdt.conf，并修改文件目录
PROJECT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)

echo "" > $SUPERVISOR_PROJECT_CONFIG_PATH
cat <<EOT >> $SUPERVISOR_PROJECT_CONFIG_PATH
[program:mousdt]
process_name=mousdt
directory=$PROJECT_DIR
command=$PROJECT_DIR/python_env/bin/uwsgi --ini $PROJECT_DIR/uwsgi.ini --http 127.0.0.1:5001
autostart=true
autorestart=true
user=www-data
numprocs=1
redirect_stderr=true
stdout_logfile=/var/log/supervisor/mousdt.log
stopsignal=INT
EOT

# 重载配置文件
supervisorctl reread
supervisorctl update
# 守护进程启动mousdt
supervisorctl start mousdt


