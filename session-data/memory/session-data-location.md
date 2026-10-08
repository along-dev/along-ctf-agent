---
name: session-data-location
description: 会话记忆与工作临时产物统一放到 session-data 目录的规则
metadata: 
  node_type: memory
  type: feedback
  originSessionId: bd52684a-801b-4451-bdc1-bbc9329cc04a
---

**规则**:所有对话/工作区的**会话记忆**与**工作临时产物**,一律放到**工作区根下的 `session-data/`** 目录,**不要散落在项目根目录,也不要与工作区同级**。子结构固定(相对工作区根):

```
session-data/
└── temp\          # 工作临时产物
    └── runs\      # main.py 等编排脚本默认输出根
```

**Why**:工作区是要打包分发的(见 PORTABLE.md)。会话记忆+临时产物是本机运行态数据,不该混进源码分发内容。放独立子目录便于打包排除、清理不误删、追溯会话产出。

**How to apply**:
- 编排脚本/工具的输出 → `session-data/temp/`(已把 `main.py` 的 `--out` 默认从 `runs` 改成 `session-data/temp/runs`)。
- 报告草稿、扫描中间结果、临时下载文件 → `session-data/temp/`。
- **不往项目根目录丢临时文件**;以前散在根目录的临时产物应迁到此处。
- 打包分发时排除 `session-data/temp/`。
- ⚠️ Claude Code 的 auto-memory 路径由 harness 按工作区标识自动落位(形如 `~/.claude/projects/<工作区标识>/memory/`),**此路径由系统决定、不可改**;`session-data/` 是"随工作区可带走"的记忆/临时归口点。相关 [[project-redteam-agent]]。
