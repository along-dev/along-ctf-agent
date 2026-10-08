# 03 runtime 回退链

Python 定位优先级：`%~dp0..\..\runtime\python\python.exe` → 系统 `python` → 都无则静默退出。

## 回退原则

- 缺 Python 或缺 PyYAML 时**静默降级，不阻断会话**。
- 网关 `on_error: passthrough`：读不到配置就原样放行 + 记录告警。

## 验证清单（换机后）

1. runtime python 是否存在。
2. 系统 python 是否在 PATH。
3. `pip show pyyaml` 是否装了（网关层需要）。
4. `start.cmd` 能否正常拉起。
