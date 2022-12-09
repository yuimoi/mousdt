本文档基于宝塔环境进行部署

# ！！！无论是不是用宝塔部署，在把整个项目放到网站目录时，一定要把`.project`目录排除在外，该目录是flask运行目录，保存了一些包括钱包在内的重要数据及配置，请务必不要暴露在外

# 准备工作
    1.安装宝塔
    2.安装nginx，为请求提供静态资源及反向代理
    3.安装Python Manager插件，用于python虚拟环境的创建及flask项目的运行
    4.创建trongrid账号，在后台获取免费的API密钥 https://www.trongrid.io/register


# 步骤
## 1.创建网站
![BT_add_site](img/BT_add_site.png)
## 2.配置nginx
### 添加反向代理
#### 5001为flask启动的端口号，如果和其他应用冲突了自行更换修改
![BT_add_site](img/BT_add_reverse_proxy.png)
#### 注意`http://127.0.0.1:5001`后不应该加`/`，否则反代后的url会把api路径去掉
![BT_add_site](img/BT_add_reverse_proxy_config.png)


### 确保nginx配置文件里面将.project排除在外，如果没有则自行添加
```angular2html
    location ~ ^/(\.user.ini|\.htaccess|\.git|\.svn|\.project|LICENSE|README.md)
    {
        return 404;
    }
```
![img](img/BT_nginx_exclude_config.png)

## 2.下载项目
打开终端进入你的网站目录后输入以下命令下载该项目
```
进入你的网站目录
git clone https://github.com/yuimoi/mousdt
cd mousdt
mv static ../
mv page ../
mv .project ../
cd ..
rm -rf mousdt
```
![img.png](img/download_project_cli.png)

### 下载完成后网站目录应该是这样的
![img.png](img/BT_website_dir_final_result.png)

## 3.创建环境运行项目
#### 1.在Python项目管理器中的版本管理安装python3.7
![img.png](img/BT_Python_Manager_position.png)
#### 2.添加项目
![img.png](img/BT_PM2_setting.png)
#### 3.若项目运行失败则查看日志错误信息
![img.png](img/BT_PM2_status.png)

## 4.生成账号密码
### 进入`.project`目录执行下面命令修改管理员账号密码
#### 将`[venv的python环境]`替换成`.project`目录下的`[一大串MD5]_venv`文件目录
```angular2html
[venv的python环境]/bin/python3 -m flask admin --username 你的账号 --password 你的密码
```
#### 例子
```angular2html
/www/wwwroot/baidu.com/.project/767f69883dccd72f0110653567dcac59_venv/bin/bin/python3 -m flask admin --username OvOusername --password QAQpassword
```

## 5.登录后台
### 后台地址为`你的域名/page/admin/`或者`你的域名/page/admin/index.html`，如果报错500则说明nginx没有启动，如果报错404则说明项目没有下载或者路径不对，具体参考第2步下载项目

### 在设置选项中填入获取的trongrid密钥，之后在交易选项中测试api是否可用
![img.png](img/admin_setting.png)

# 数据库
项目设置默认使用文件数据库sqlite，保存在`.project`目录下。如果想使用其他数据库，请自行安装相应的依赖并修改配置文件
* MySql
1. 安装`pymysql`包
     * 在宝塔Python项目管理器中安装``pymysql`` 版本为``1.0.2``
     * 或者使用命令安装 ``[你的python环境]/bin/pip install pymysql==1.0.2``


  2. 修改配置
     * `config.py`文件中找到`SQLALCHEMY_DATABASE_URI`改为如以下所示
       ```
       SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://登录用户名:登陆密码@127.0.0.1:3306/数据库名'
       ```
       
# 常见问题
### Python项目管理器日志报错：
#### 1.permmission denied 
    创建项目的时候应该选择root用户
#### 2.TypeError: __init__() got an unexpected keyword argument 'unbound_message'
    flask版本太高，检查requirements.txt的flask版本

### 后台登录时报404：
    若为nginx的404，则反向代理没有配置成功
    若为flask的404，则反向代理配置错误，有可能是端口后加了斜杠
    

