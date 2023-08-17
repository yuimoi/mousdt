# 测试项目，仅供参考和学习，勿用于生产环境

**NOTE: 本项目心血来潮写的，再次回看发现存在很多问题，代码仅供学习和交流，如有需要可以来看看我的[恰饭线上版](https://mopay.vip/)。**

# moUSDT
一个使用Flask开发的USDT收款平台，通过HTTP接口进行订单的发起及回调，自带网页管理后台管理及查询订单、钱包、及链上交易，后台管理页面使用[vue-element-admin](https://github.com/PanJiaChen/vue-element-admin)搭建


# moUSDT目前
* 支持在规定时间内`多次`小额转账完成订单,订单支持`任意金额`
* 后台管理钱包自带转账功能
* 钱包`本地`随机生成，交易`离线`签名，与`密钥`相关操作均离线进行，降低泄露风险
* 批量生成钱包,批量导出钱包，手动导入钱包，钱包优先级设置，优先使用有余额的钱包
* 数据库使用文件数据库sqlite，方便搭建
* 支持TRON链的USDT，使用trongrid查询链上交易，允许一定的网络波动导致的请求错误
* 仅在有未付款订单时进行api查询，减小api请求资源消耗
* 自带了易支付规则的支付接口

# 演示DEMO
https://user-images.githubusercontent.com/119736684/206887487-9ad4ebcc-5883-4f6c-aa59-0d70b1737327.mp4



# 项目结构
```angular2html
.project    # 后端代码
page        # 前端页面
├──pay───── # 支付页面前端代码
└──admin─── # 后台管理页面前端代码
static      # 静态文件
```

# 安装教程
- [脚本安装教程](wiki/MANUALLY_RUN.md)
- [宝塔安装教程](wiki/BT_RUN.md)
- 后台登录地址：`你的域名/page/admin`或`你的域名/page/admin/index.html`

# 安全说明：
    1 .project路径下的文件为运行文件，请不要暴漏给外部（不会配置的就不要把文件放到nginx网站目录下）
    2 请对自己的信息和服务器负责，使用强度高的登录用户名及密码
    3 Order表中储存了订单发起方未转义的数据，所以请不要把密钥随意泄露，虽然vue解析页面有XSS防护，但是还是防患于未然
    
# 接口配置文档
    1.易支付(参考彩虹易支付)
        ①商户id：（随便填）
        ②商户密钥：（登录后台的设置界面查看）
        ③接口地址：你的域名/api/pay/epay/submit.php

    2.更多支付接口随后添加……

# 操作命令
#### 以下操作默认在`.project`目录下进行，python3命令自行替换成自己的python环境（若使用宝塔Python项目管理器则环境在`.project`目录下的`[MD5字符串]_venv`中）

### DEBUG模式运行项目（生产环境不要用）
    python3 -m flask run --port 5001 --debugger
    并将config.py中的DEBUG改为True

### 修改后台登录账号密码
    python3 -m flask admin --username 你的用户名 --password 你的密码

### 导出钱包数据
    python3 -m flask dump_wallet

### 清除所有运行数据（谨慎运行，请事先将钱包等重要数据下载到本地）
    python3 -m flask clear_data

# 有问题反馈
在使用中有任何问题，欢迎反馈给我，可以用以下联系方式跟我交流
* tg: [@nulllllllll](https://t.me/nulllllllll)


# 感激
灵感来自以下的项目

* [epusdt](https://github.com/assimon/epusdt)
