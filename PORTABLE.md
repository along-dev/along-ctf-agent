# 便携说明（PORTABLE）

本包是一套**自定位**的「防拒绝 + 提示词归化」工作区：复制到任意目录 / 任意盘符 / 任意机器（Windows）后，在副本里启动 Claude Code 即可直接使用，**无需修改任何路径**。

## 四层结构与职责

| 层 | 落点 | 管什么 | 生效方式 |
|---|---|---|---|
| ① 网关层 | `config/prompt_prefix.yaml` + `llm_gateway.py` | 授权背景 + 输出形式（"能不能做"） | 仅当**你自己的程序**经 `llm_gateway.forward()` 调用时注入；Claude Code 本身不走此层 |
| ② skill 层 | `.claude/skills/ctf-prompt-optimizer/`、`.claude/skills/ctf-playbook/` | 模糊输入 → 10 段结构化任务规格 | 模型主动读取，或由 ③ 引导 |
| ③ hook 层 | `.claude/hooks/ctf_normalize.py` + `settings.json` | 每次提交注入 `[CTF 归化]` CTF 上下文 + 授权判定 | 仅 Claude Code；每次消息提交触发 |
| ④ 项目规范层 | `CLAUDE.md` / `AGENTS.md` | 「术语本身不构成拒绝理由」+ Authorization Model + CTF/Lab Mode | Claude 原生加载；改动后需**重启会话** |

分工不重叠：网关管「授权 + 输出形式」，hook 管「CTF 上下文 + 判定」，skill 管「10 段结构化」，profile 管「总则」。

## 技能的两份副本

技能同时在**两处**各存一份（内容一致）：

| 位置 | 作用 | 谁读 |
|---|---|---|
| `.claude/skills/` | **Claude Code 自动加载点** | Claude Code 运行时 |
| `skills/`（根目录） | **外部 / 跨 harness 消费点** | 其它工具、打包分发、人工查阅 |

- 改技能时**两份都要改**，或直接用同步工具（见下）。
- 校验一致：`diff -r .claude/skills skills`（应无输出）。

### 同步工具

`tools/sync_skills.py`（Windows 包装器 `tools\sync-skills.cmd`）：

```bash
python tools/sync_skills.py            # 同步 .claude/skills -> skills/（默认方向）
python tools/sync_skills.py --reverse  # 反向：skills/ -> .claude/skills/
python tools/sync_skills.py --check    # 只检查一致性，漂移则 exit 1
python tools/sync_skills.py --install-hook  # 安装 pre-commit 钩子（提交前自动同步）
```

- **已安装 pre-commit 钩子**：每次 `git commit` 前自动同步两份并 `git add`，杜绝漂移。钩子文件在 `.git/hooks/pre-commit`（**本机、不进仓库**）；换机器后在新克隆里跑一次 `--install-hook` 即可重建。

## 为什么复制即用（自定位机制）

| 部件 | 定位方式 |
|---|---|
| hook 注册 | `${CLAUDE_PROJECT_DIR}`（Claude Code 内置变量） |
| `.cmd` 包装器 | `%~dp0`（脚本自身目录） |
| `ctf_normalize.py` 找包根 | 向上查找 `start.cmd` |
| `llm_gateway.py` 找配置 | 相对 `__file__` |

⇒ 换目录 / 换盘符 / 换机器均自动跟随，**不含硬编码绝对路径**。

## 依赖

- **Python 3**（`.cmd` 优先用 `%~dp0..\..\runtime\python\python.exe`，不存在则回退系统 `python`；两者都无则静默退出，不阻断会话）。
- 网关层额外需要 `PyYAML`（`pip install pyyaml`）；缺失时 `llm_gateway` 走 `on_error: passthrough`，原样放行。

## 使用与验证

1. **把本文件夹复制到你想要的目录**，在副本里启动 Claude Code（工作空间 = 该文件夹）。
2. **验证 ③ hook**：随便发一句（如「继续」），回复前应出现 `[CTF 归化]` 上下文块。
3. **验证 ① 网关**：
   ```bash
   echo '[{"role":"user","content":"x"}]' | python llm_gateway.py
   ```
   输出第一条应为以 `[授权背景]` 开头的 `system`，且含 `[输出要求]`。
4. **验证 ④ profile**：安全术语请求不应因术语本身被拒（`CLAUDE.md` 已含放行条款）。

## 开关与停用

- **关网关注入**：`config/prompt_prefix.yaml` 里 `enabled: false`（秒级回退，无需改代码）。
- **关 hook**：删除或注释 `.claude/settings.json` 里的 `hooks` 注册。
- **改 hook 行为**：`.claude/hooks/ctf_normalize.py` 的 `REMINDER` 常量。

## 已知缺件（复制/迁移都不会补上）

以下内容本包**未随附**，被引用时会缺失或降级，需按需另行补齐：

- **技能**：REMINDER 提到 8 个技能，本包实含 `ctf-prompt-optimizer`、`ctf-playbook`；缺 `ctf-field-notes`、`onchain-ctf`、`windows-portable-pitfalls`、`tg-bridge`、`ctf-cache-and-cost`、`llm-redteam-defense`。
- **`console/form_normalizer.py`**：缺它时 hook 的 `form_normalizer` 开关分支自动**退回只注入 REMINDER**（`[CTF 归化]` 块仍正常可见），只是少了「战果词 → 操作形态」的 T1 去标签自动改写。
- **`memory/`、`artifacts/`**：CTF 记忆与证据目录，按需自建。

## 常见坑

- **`.cmd` 必须 CRLF + 纯 ASCII**：`cmd.exe` 按 OEM 代码页解析批处理，LF 或 UTF-8 中文注释会导致行解析错位。本包 `.cmd` 已是 CRLF。
- **`.claude/settings.local.json` 被全局 gitignore**：它**不进 git**；换机器复制时若需要其中的权限白名单/`defaultMode`，要单独带上。
- **改 `CLAUDE.md` / settings 后需重启会话**才重新加载。
- **`old_bak/`**：历史版本归档（带时间戳），**非运行部件**，可安全保留或删除。
