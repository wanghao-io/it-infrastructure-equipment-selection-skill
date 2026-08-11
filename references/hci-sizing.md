# HCI Sizing Reference

## Principles

超融合设计需要同时考虑性能和故障能力。

## N+1 Validation

检查：

- 单节点故障后CPU是否满足
- 单节点故障后内存是否满足
- 存储副本是否完整
- 网络是否存在瓶颈

## Typical Design

中小型工业项目通常采用3节点起步，但必须根据业务负载验证。

## Output

- 节点数量
- 每节点配置
- 可用资源
- 故障后资源
- 扩展能力
