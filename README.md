# moUSDT
一个使用Flask开发的USDT收款平台，通过HTTP接口进行订单的发起及回调，自带网页管理后台管理及查询订单、钱包、及链上交易，后台管理页面使用[vue-element-admin](https://github.com/PanJiaChen/vue-element-admin)搭建


# moUSDT目前
* 数据库使用文件数据库sqlite，方便搭建
* 支持在规定时间内`多次`小额转账完成订单
* 订单支持`任意金额`
* 钱包`本地`随机生成，与`密钥`相关操作均使用`tronpy`包离线进行，降低泄露风险
* 批量生成钱包,批量导出钱包，手动导入钱包，钱包优先级设置，优先使用有余额的钱包
* 支持TRON链的USDT，使用trongrid查询链上交易，允许一定的网络波动导致的请求错误
* 仅在有未付款订单时进行api查询，减小api请求资源消耗
* 自带了易支付规则的接口

# 演示DEMO
https://user-images.githubusercontent.com/119736684/205488390-7c0e75dd-b42a-46eb-b644-3252020a682e.mp4


# 项目结构
```angular2html
.project    # 后端代码
page        # 前端页面
├──pay───── # 支付页面前端代码
└──admin─── # 后台管理页面前端代码
static      # 静态文件
```

# 安装教程
- [宝塔安装教程](wiki/BT_RUN.md)
- 后台登录地址：`你的域名/page/admin`或`你的域名/page/admin/index.html`

# 接口配置文档
    1.易支付(参考彩虹易支付)
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
