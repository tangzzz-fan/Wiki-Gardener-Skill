# 域档案：iOS

## 局部宪章

- 收录侧重：CoreBluetooth / 配网实战结论
- 深度定位：工程实战

## 术语表

- 高辨识：CoreBluetooth、CBCentralManager、BLE 配网、peripheral
- 通用：配网、扫描、连接

## 时效性锚点

| 项 | 当前版本/状态 | 更新日期 |
|---|---|---|
| iOS | 18.x | 2026-07-01 |
| Xcode | 16.x | 2026-07-01 |

## 领域 Smell 清单

- 在主线程阻塞等待 CBCentralManager 回调
- 把 `CBCentralManagerScanOptionAllowDuplicatesKey` 当生产默认开启

## 写作立场

- 视角：第一人称工程实战记录
- 深度基线：写到可落地的决策与边界条件
- 偏好写法：先结论后论证；代码片段必附适用版本
- 避免写法：教科书式定义堆砌

## 常见误区

- 认为 BLE 扫描在后台与前台行为一致
- 把 RSSI 阈值当成设备身份
