---
title: CB 回调里同步干重活会卡主线程，只投递，重活丢后台
domain: ios
status: draft
origin: chat
---

# CB 回调里同步干重活会卡主线程，只投递，重活丢后台

环境钉在 iOS 18.x / Xcode 16.x，对象是 CoreBluetooth。我在 `CBCentralManager` 或 peripheral 的回调里同步做文件 IO、大块 JSON 解析，或任何会堵上百毫秒的活，主线程和界面会一起卡死。后来定下的规矩很窄。回调里只记状态、只投递任务。重活放到我自己的后台队列。

## 我踩到的现象

有一次在 `centralManagerDidUpdateState` 里，看到 poweredOn 就同步读本地配置，读完再调用 `scanForPeripherals`。仪表盘上主线程卡了大约 2 秒，界面跟着冻。状态到了再扫描，这个顺序没错。错在把整段启动路径塞进了 CB 回调的同步执行。

域档案里那条 Smell 写的是，不要在主线程阻塞等待 CBCentralManager 回调。我后来觉得它和「回调里自己堵主线程」是一家。等的时候堵，回调里堵，界面都会掉帧。

## 可以复述的结论

CB 回调默认按主线程语义来想。自己初始化 `CBCentralManager` 时显式传了 queue 的除外。没传就按主队列处理。

回调体里我只允许三件事。改自己的状态机字段。用 `DispatchQueue` 投递。发很轻的通知。

文件、网络、大解析、长锁，全部出队后再做。做完再进入「可以启动扫描」或「可以连接」的下一步。

## 落地写法

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

`bleWorkQueue` 用自己的串行队列，免得和主线程抢。回到主线程再碰 UI，以及「启动扫描」这类仍要跟 CB 生命周期合拍的动作。就算创建 manager 时已经传了后台 queue，回调里也不要同步读盘。队列不挡主线程，照样可以把回调拖得很长。

## 两条红线

不要在主线程上，或任何你还要保持响应的线程上，阻塞等待下一次 CB 回调。用状态机接着跑，不要 `sleep`，也不要信号量死等。

生产扫描不要默认打开 `CBCentralManagerScanOptionAllowDuplicatesKey`。它会抬高回调频率，把回调里一点点同步成本放大成持续卡顿。真要调试，再临时打开。

## 和库内笔记怎么分工

[[BLE 配网踩坑记录]] 讲配网四段和模组断连容忍。本篇不写协议步骤。

[[CoreBluetooth 扫描过滤]] 讲 UUID 和 RSSI 过滤。本篇不写过滤策略。

本篇只钉两件事。回调的线程纪律。启动扫描前，重活放在哪。

## 挂载建议

上级 MOC 挂 [[ios-moc]]，或从总 MOC 进 iOS。建议互链 [[BLE 配网踩坑记录]] 与 [[CoreBluetooth 扫描过滤]]。

官方若对「未指定 queue 时回调落在哪条线程」的表述有版本差，标 [待核验]。以创建 manager 时传入的 `queue:` 为准。本文按常见主队列默认来写。
