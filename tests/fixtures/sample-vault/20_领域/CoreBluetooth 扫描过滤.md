---
title: CoreBluetooth 扫描过滤
domain: ios
status: evergreen
origin: human
---

# CoreBluetooth 扫描过滤

结论：生产环境默认用 service UUID 过滤扫描；仅在排障时短暂打开 AllowDuplicates。

全量扫描会显著抬高耗电，且回调风暴容易把状态机冲乱。排障会话结束后必须恢复过滤策略。
