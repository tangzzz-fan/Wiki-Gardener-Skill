---
title: iOS 蓝牙自定义协议（草稿）
domain: ios
status: draft
origin: draft
---

# iOS 蓝牙自定义协议（草稿）

结论：配网之后用私有帧在 characteristic 上收发就能完成业务同步。

随便记一下：连上 peripheral 以后直接 writeValue，不用管 MTU 和分片；回调里解析长度字段，错了再重发就行。主线程里同步等通知也没关系，协议简单。

（评测用有意瑕疵稿：未分类；缺系统版本/真机环境；忽略 MTU 分片与错误恢复；主线程同步等待——用于 A2b「相关补缺 + 先审再挂」。库内已有 BLE 配网笔记但不含自定义协议。）
