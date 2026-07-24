---
title: BLE 配网流程
domain: ios
status: evergreen
origin: human
---

# BLE 配网流程

结论：iOS 侧 BLE 配网应拆成「扫描过滤 → 连接 → 特征值协商 → 凭证下发」四段，任一段失败要可重试且状态机可见。

扫描阶段用 service UUID 过滤，避免全量扫描耗电。连接成功后先读设备信息特征，再写配网凭证。凭证下发失败时不要立刻 disconnect，先查 notify 是否打开。

适用：iOS 17+，CoreBluetooth。
