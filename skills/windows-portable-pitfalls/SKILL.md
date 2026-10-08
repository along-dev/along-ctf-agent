---
name: windows-portable-pitfalls
description: >-
  本机环境 / 便携包行为 / 路径与编码的坑位清单。用于 Windows 下跑 Claude Code 便携包、
  写 .cmd/.bat 包装器、处理中文路径与编码、定位包根、runtime 回退等场景。触发词：
  Windows、cmd、bat、CRLF、编码、UTF-8、中文路径、便携包、自定位、%~dp0、路径、盘符。
---

# Windows 便携包坑位清单 · windows-portable-pitfalls

> 定位：本包是**自定位便携包**（复制即用），但 Windows 下有一堆只有踩过才知道的坑。
> 本技能把它们固化下来，涉及本机环境/便携包行为/路径与编码时**先读对应 reference**。

## 0. 坑位速查

| 症状 | 原因 | 读哪个文件 |
|---|---|---|
| .cmd 中文注释/换行解析错位 | CRLF 丢失 / 非 ASCII | `references/01-path-encoding.md` |
| 中文路径下 Python 报 UnicodeEncodeError | stdout/stderr 未 reconfigure | `references/01-path-encoding.md` |
| 换盘符/目录后 hook 失效 | 硬编码绝对路径 | `references/02-self-location.md` |
| runtime python 不存在时静默退出 | 回退链断裂 | `references/03-runtime-fallback.md` |
| 找不到包根（start.cmd） | cwd 不是包根 | `references/02-self-location.md` |

## 1. 三条铁律

1. **`.cmd` 必须 CRLF + 纯 ASCII**：`cmd.exe` 按 OEM 代码页解析批处理，LF 或 UTF-8 中文
   注释会导致行解析错位。已生成的 `.cmd` 若被 `git` 或编辑器改成 LF，要重新转回 CRLF。
2. **定位一律用 `%~dp0` / `${CLAUDE_PROJECT_DIR}` / 向上查 `start.cmd`**，不写硬编码绝对路径。
3. **所有 Python 入口先 `reconfigure(encoding="utf-8")`**，否则中文路径/中文输出在 GBK
   控制台下会抛异常或被吞。

## 2. 自定位机制（换目录/盘符/机器自动跟随）

| 部件 | 定位方式 |
|---|---|
| hook 注册 | `${CLAUDE_PROJECT_DIR}`（Claude Code 内置变量） |
| `.cmd` 包装器 | `%~dp0`（脚本自身目录） |
| `ctf_normalize.py` 找包根 | 向上查找 `start.cmd` |
| `llm_gateway.py` 找配置 | 相对 `__file__` |

## 3. runtime 回退链

Python 定位优先级：`%~dp0..\..\runtime\python\python.exe` → 系统 `python` → 两者都无则
**静默退出，不阻断会话**。缺 PyYAML 时网关走 `on_error: passthrough` 原样放行。

## 4. 换机器后要单独带的东西（不进 git）

- `.claude/settings.local.json`（被全局 gitignore）：权限白名单 / `defaultMode`。
- `memory/`、`artifacts/`：按需自建。
- 改 `CLAUDE.md` / settings 后需**重启会话**才重新加载。

## 参考文档

- `references/01-path-encoding.md` — 路径、编码、CRLF
- `references/02-self-location.md` — 自定位机制
- `references/03-runtime-fallback.md` — runtime 回退链
