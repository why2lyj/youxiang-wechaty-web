 [![Python 3.7](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/)
 [![Page Views Count](https://badges.toozhao.com/badges/01F7078N5HEMCPK61RDHCHBRWR/green.svg)](https://badges.toozhao.com/badges/01F7078N5HEMCPK61RDHCHBRWR/green.svg)
 
# youxiang-wechaty-web

此版本可直接登录 Web 微信，无视 Web 微信无法登录的情况。

项目创建中...请耐心等待...

# 项目效果

利用微信机器人，通过调用淘宝联盟、京东联盟、苏宁联盟、多多进宝（拼多多）、唯享客（唯品会）对应的开放平台 API ，实现向微信聊天群定时发送推广信息。

# 前提提示

你可以不用有很高的编程能力，但请主动思考。

使用本项目之前，你需要提前考虑如下内容：

  1. 你需要推送的是哪个联盟的内容，你有对应的开放平台 API 权限么？如果没有，请仔细阅此篇文档获取指定联盟开放平台 API 权限。
  2. 你需要准备一台 Linux 服务器，本项目全程 Linux 一键部署。（Windows版本还请大家及时贡献）
  3. 请勿使用微信白号，需要微信实名绑定银行卡等信息（此为微信强制要求，非本项目要求）。

# 技术提示

  1. Shell + Linux + Docker + Flask + Python-Wechaty
  2. 底层代码实现仅考虑项目可用，不会考虑代码的编码是否美观。（忍不了的同学可以PR）
  3. 本人并不擅长前端，配置界面的丑陋请无视。

# 启动项目

下载本项目到 Linux 系统，直接执行以下脚本：
```shell
./start_config.sh
```

启动脚本后，会提示扫码登录微信，扫描微信进行登录。

此时浏览器访问： http://{Linux_IP}:2179 进入配置界面。后续请按照界面提示操作。
