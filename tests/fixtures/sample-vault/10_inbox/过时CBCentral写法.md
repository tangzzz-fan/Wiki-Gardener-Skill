---
title: 过时的 CBCentral 写法
domain: ios
status: draft
origin: draft
---

# 过时的 CBCentral 写法

结论：在 `viewDidLoad` 里同步等待 `CBCentralManager` 状态变成 poweredOn，再用 `sleep` 轮询。

（故意错误：阻塞主线程等待回调，用于审查模式评测。）
