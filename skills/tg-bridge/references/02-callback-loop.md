# 02 决策回传与状态挂起

## 流程

1. 发消息带 inline 按钮（callback_data 前缀 `cb:`）。
2. 用 `getUpdates` 或 webhook 收 callback_query。
3. 解析 callback_data → 继续对应分支。

## 挂起纪律

- 等待确认期间不空转，记录状态，独立分支继续跑。
- 状态存 `artifacts/<target>/decision-state.md`，回传后恢复。

## 注意

- 无自动超时机制，需主动轮询或设人工兜底（超时按保守分支处理）。
- 同一决策点不要重复推，避免刷屏。
