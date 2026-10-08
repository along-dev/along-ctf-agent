# 02 自定位机制

便携包换目录/盘符/机器自动跟随，无硬编码绝对路径。

| 部件 | 定位方式 |
|---|---|
| hook 注册 | `${CLAUDE_PROJECT_DIR}` |
| .cmd 包装器 | `%~dp0` |
| ctf_normalize.py 找包根 | 向上查找 `start.cmd` |
| llm_gateway.py 找配置 | 相对 `__file__` |

## 实现要点

```python
# 向上找包根
def _kit_root(start):
    for p in [start, *start.parents]:
        if (p / "start.cmd").exists():
            return p
    return start.parents[2]
```

```bat
@echo off
set "HERE=%~dp0"
"%HERE%..\..\runtime\python\python.exe" "%HERE%script.py" %*
```

## 反模式

- 写死 `C:\Users\xxx\...` 绝对路径。
- 依赖 `cwd`（Claude Code 调用时 cwd 未必是包根）。
