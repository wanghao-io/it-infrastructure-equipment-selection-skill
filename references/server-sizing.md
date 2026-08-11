# Server Sizing Reference

## Purpose

服务器选型必须从业务负载开始，而不是从型号开始。

## CPU

考虑因素：

- 虚拟机数量
- vCPU需求
- 物理核心数量
- 超配比例
- 数据库负载
- SCADA/历史库负载
- 扩展余量

输出：

- 最低配置
- 推荐配置
- 扩展配置

## Memory

内存估算：

业务内存 + 数据库缓存 + 虚拟化开销 + 故障余量 + 扩展空间

## Storage

必须区分：

- Raw Capacity
- Usable Capacity
- RAID/副本开销
- 快照空间
- 增长率

## Checklist

- [ ] CPU架构确认
- [ ] 内存扩展能力
- [ ] 存储接口确认
- [ ] 网络接口确认
- [ ] 维保周期确认
