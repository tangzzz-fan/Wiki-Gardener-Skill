---
title: MQTT QoS 选型
domain: iot
status: evergreen
origin: human
---

# MQTT QoS 选型

结论：设备遥测默认 QoS 0 或 1；配置下发用 QoS 1；只有对端无法幂等时才考虑 QoS 2。

QoS 2 的握手成本高，在弱网嵌入式设备上往往得不偿失。先问「重复消费能否接受」，再选等级。
