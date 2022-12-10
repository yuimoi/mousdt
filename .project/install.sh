#!/bin/bash

# 安装编译python3的依赖
if awk -F= '/^NAME/{print $2}' /etc/os-release | grep -qi 'centos'; then
	yum update -y
	yum -y install wget yum-utils gcc install zlib-devel openssl-devel bzip2-devel libffi-devel sqlite-devel

  # centos添加www-data用户
  adduser www-data

elif awk -F= '/^NAME/{print $2}' /etc/os-release | grep -qi 'ubuntu\|debian'; then
	apt-get update -y
	apt-get install wget build-essential zlib1g-dev libssl-dev libncursesw5-dev libreadline-gplv2-dev libssl-dev libgdbm-dev libc6-dev libsqlite3-dev libbz2-dev libffi-dev -y
fi


FORCE_INSTALL_PYTHON=false
FORCE_INSTALL_REQUIREMENTS=false

set -e
PROJECT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd) 
PROJECT_PARENT_DIR="$(dirname "$PROJECT_DIR")"

# 删除解压的python文件
function cleanup {
  rm -rf $PROJECT_DIR/install/Python-3.7.12.tar
  rm -rf $PROJECT_DIR/install/Python-3.7.12
}
trap cleanup EXIT

# 编译python3
if [ ! -f "$PROJECT_DIR/python_env/bin/pip3" ] || $FORCE_INSTALL_PYTHON; then
    cd install
    xz -dk Python-3.7.12.tar.xz || true
    tar -xvf Python-3.7.12.tar
    cd Python-3.7.12
    ./configure --prefix=$PROJECT_DIR/python_env
    make && make install
fi

# 安装mousdt依赖
if [ ! -f "$PROJECT_DIR/python_env/bin/uwsgi" ] || $FORCE_INSTALL_REQUIREMENTS; then
    $PROJECT_DIR/python_env/bin/pip3 install -r $PROJECT_DIR/requirements.txt
fi

# 修改uwsgi配置文件
sed -i "s|PROJECT_DIR|$PROJECT_DIR|g" "$PROJECT_DIR/uwsgi.ini"
sed -i "s|PROJECT_PARENT_DIR|$PROJECT_PARENT_DIR|g" "$PROJECT_DIR/uwsgi.ini"




