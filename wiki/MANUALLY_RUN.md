# 本教程手动安装基于已经写好的脚本，不放心的可以看着脚本自己写，脚本途中出现报错的可以照着报错信息修复，也可以报告给我修复完善脚本
## 安全说明：
    1 .project路径下的文件为运行文件，请不要暴漏给外部（不会配置的就不要把文件放到nginx网站目录下）
    2 请对自己的信息和服务器负责，使用强度高的登录用户名及密码


### 以下脚本仅在centos7、ubuntu18、debian9做过测试，其他发行版请自行照着脚本安装
### debian没有sudo的话可以去掉命令前面的sudo
# 1. 安装编译python3的依赖库，编译安装python3，安装mousdt所需的python依赖，
```
cd /home # 进入一个安装mousdt的目录
mkdir mousdt
cd mousdt
wget https://github.com/yuimoi/mousdt/releases/download/0.0.1/mousdt_0.0.1_release.tar.gz
sudo tar -xzf mousdt_0.0.1_release.tar.gz
rm -f mousdt_0.0.1_release.tar.gz
cd .project
sudo bash install.sh
```

### 执行后如果可以使用以下命令成功执行并访问，则说明安装成功(ctrl+c关闭运行) 
#### 访问地址为：你的ip:5001/page/admin/index.html
    python_env/bin/uwsgi --ini uwsgi.ini --http 0.0.0.0:5001
### 若上一步运行成功，则此时在`.project`目录下可使用以下命令修改登录的用户名或密码
    python_env/bin/python3 -m flask admin --username 你的用户名 --password 你的密码



# 2. 为mousdt创建守护进程和开机启动（该守护进程配置无法通过ip访问，只能从nginx反向代理访问）
### 以下命令安装并启动守护进行
    sudo bash supervisor.sh
### 查看运行结果，如果出现方框围住的mousdt，则说明守护进程运行成功
    supervisorctl tail mousdt

# 3. Ningx反向代理
### 反向代理不用配置路径，将所有请求发送给5001端口即可
#### 参考配置
```angular2html
location ^~ /
{
    proxy_pass http://127.0.0.1:5001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header REMOTE-HOST $remote_addr;

    add_header X-Cache $upstream_cache_status;

}
```

# 守护进程操作
   * 停止mousdt守护进程\
       ```supervisorctl stop mousdt```
   * 启动mousdt守护进程\
       ```supervisorctl start mousdt```
   * 重启mousdt守护进程\
       ```supervisorctl restart mousdt```

   * 删除mousdt守护进程配置（下次重启不会启动）
     * centos
          ```rm -f /etc/supervisord.d/mousdt.ini```
     * ubuntu\debian
          ```rm -f /etc/supervisor/conf.d/mousdt.conf```
