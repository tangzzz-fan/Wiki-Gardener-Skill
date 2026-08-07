---
title: CB 回调里同步干重活会卡主线程——只投递，重活丢后台
domain: ios
status: draft
origin: chat
---

# CB 回调里同步干重活会卡主线程——只投递，重活丢后台

适用：iOS 18.x / Xcode 16.x（CoreBluetooth）。结论直接说：在 `CBCentralManager` / peripheral 回调里同步做文件 IO、JSON 大解析或任何会堵上百毫秒的事，等于拿主线程赌 UI；正确做法是回调里只做状态记录与任务投递，重活放到你自己的后台队列。

## 我踩到的现象

有一次在 `centralManagerDidUpdateState` 里，看到 poweredOn 就同步读本地配置文件，读完再 `scanForPeripherals`。仪表盘上主线程卡了大约 2 秒，界面跟着冻。逻辑「没错」——状态到了才扫描——但把启动路径塞进了 CB 回调同步路径。

这和域档案里的 Smell「在主线程阻塞等待 CBCentralManager 回调」是同一家族：要么你在等回调时堵主线程，要么你在回调里堵主线程。两端都会让界面和系统看你不顺眼。

## 结论（可复述）

1. CB 回调默认按主线程语义想（你自己 `CBCentralManager` 初始化时指定的 queue 除外；若未显式传 queue，按主队列处理）。  
2. 回调体只允许：改自己的状态机字段、`DispatchQueue` 投递、发很轻的通知。  
3. 文件、网络、大解析、长锁——全部出队后再做；做完再回到「可启动扫描 / 可连接」的下一步。

## 落地写法（示意）

```swift
// iOS 18 / Xcode 16
func centralManagerDidUpdateState(_ central: CBCentralManager) {
    switch central.state {
    case .poweredOn:
        // 轻：记状态
        self.blePoweredOn = true
        // 重：读配置 + 决定是否扫描，丢自己的队列
        self.bleWorkQueue.async { [weak self] in
            guard let self else { return }
            let config = self.loadScanConfigFromDisk() // 重活
            DispatchQueue.main.async {
                self.startScanIfNeeded(config)
            }
        }
    default:
        self.blePoweredOn = false
        self.stopScanForPowerLoss()
    }
}
```

`bleWorkQueue` 用自己的串行队列即可，避免和主线程抢；回到主线程再碰 UI 与「启动扫描」这类仍需与 CB 生命周期对齐的动作。若你创建 `CBCentralManager` 时就传了后台 queue，仍不要在回调里同步读盘——队列不阻塞「主线程」不等于可以无限拖长回调占用。

## 两条红线

- 不要在主线程（或任意你还要保持响应的线程）上阻塞等待下一次 CB 回调。用状态机 + 续跑，不靠 `sleep` / 信号量死等。  
- 生产扫描不要默认打开 `CBCentralManagerScanOptionAllowDuplicatesKey`；它放大回调频率，会把「回调里一点点同步成本」放大成持续卡顿。调试需要时再临时开。

## 和库内笔记的分工

- [[BLE 配网踩坑记录]]：讲配网四段与模组断连容忍——本篇不重复协议步骤。  
- [[CoreBluetooth 扫描过滤]]：讲 UUID / RSSI 过滤——本篇不讲过滤策略。  
- 本篇只钉死：回调线程纪律与「启动扫描前」的重活位置。

## 挂载建议

- 上级 MOC：[[ios-moc]]（或总 MOC → iOS）  
- 建议互链：[[BLE 配网踩坑记录]]、[[CoreBluetooth 扫描过滤]]  

若官方对「未指定 queue 时回调线程」表述有版本差，标为 [待核验]：以你创建 manager 时传入的 `queue:` 实参为准，本文按常见主队列默认讨论。
