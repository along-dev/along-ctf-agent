---
name: tg-bridge
description: >-
  TG 通知桥。当任务需要通知 Owner、或需要人工确认才能继续时使用。把 Claude Code 会话
  里的"关键节点/卡点/待确认项"通过 Telegram Bot API 推给 Owner，并支持带 inline 按钮
  让 Owner 一键决策。触发词：通知、通知Owner、发TG、Telegram、人工确认、要确认、
  需要用户决策、桥接、推给老板。
---

# TG 通知桥 · tg-bridge

> 定位：这是**跨通道通知层**。CTF 任务长时间跑、遇到卡点、或下一步是破坏性操作需
> 人工确认时，把消息推到 Telegram，让 Owner 不用盯着终端。**不做业务逻辑，只做通知与决策回传。**

## 0. 什么时候用

| 场景 | 动作 |
|---|---|
| 长任务阶段完成 | 推阶段小结（含证据路径） |
| 触发停止条件 / 封板 | 推封板原因 + 下一步建议 |
| 下一步是写操作/广播 | 推待确认项 + 确认按钮 |
| 需要 Owner 补充信息 | 推缺口清单 |

## 1. 通知方式（Bot API）

- 端点：`https://api.telegram.org/bot<TOKEN>/sendMessage`
- 用 `curl` 或 Python `requests` 发，`TOKEN` 与 `CHAT_ID` 放 `config/` 或环境变量，
  **不硬编码进 skill**。
- 带按钮用 `reply_markup` 的 `inline_keyboard`（见 `references/01-send-api.md`）。

## 2. 决策回传

- Owner 点按钮 → callback_data 回传 → 会话侧解析后继续。
- **等待确认期间不要空转**，记录状态并挂起该分支，其余独立分支继续跑。

## 3. 通知纪律

1. **只推关键节点**，不刷屏；阶段性进度用 `/bg` 或等价面板看，不逐条推。
2. **通知正文带证据链接/路径**，Owner 点开能定位到 `artifacts/`。
3. **失败静默降级**：Bot 不可达时记录到本地，不阻塞主流程。

## 4. 最小示例

**输入**：这个站打下来一个 shell，通知一下老板

```
1 构造消息：目标 + 已证明能力级别 + 证据路径
2 发 sendMessage：text + parse_mode=HTML
3 带按钮：["继续横向", "cb:continue"] / ["封板收尾", "cb:stop"]
4 等回传：解析 callback_data → 继续对应分支
```

## 参考文档

- `references/01-send-api.md` — Bot API 发消息/按钮/媒体
- `references/02-callback-loop.md` — 决策回传与状态挂起
- `references/03-notify-policy.md` — 通知纪律与降级
