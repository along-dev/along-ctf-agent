# 03 通知纪律与降级

## 只推关键节点

- 阶段完成、触发停止条件、待确认写操作、需要补充信息。
- 逐条进度不推（面板看），不刷屏。

## 降级

- Bot 不可达 → 记录到本地 `artifacts/<target>/notify-log.md`，不阻塞。

## 消息模板

```
[阶段完成] <target>
- 证明级别：<observed/primitive>
- 证据：<artifacts 路径>
- 下一步：<建议>
```
