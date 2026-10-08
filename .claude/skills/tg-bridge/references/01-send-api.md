# 01 Bot API 发消息/按钮/媒体

## 基础发送

```python
import requests
TOKEN = "<TOKEN>"; CHAT_ID = "<CHAT_ID>"
def send(text, buttons=None):
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": buttons}
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload, timeout=15)
```

## 按钮格式

```python
# 每内层数组 = 一行
buttons = [
    [["继续横向", "cb:continue"], ["封板收尾", "cb:stop"]],
    [{"text": "打开报告", "url": "https://..."}],
]
```

## 凭据管理

- TOKEN / CHAT_ID 放 `config/` 或环境变量，**不硬编码进 skill / 不进 git**。
- 失败静默降级：记录本地，不阻塞主流程。
