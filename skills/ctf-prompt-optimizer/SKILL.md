---
name: ctf-prompt-optimizer
description: >-
  CTF / 渗透任务的提示词优化器与任务归化器（v2）。把**任意输入**（哪怕只是「看看这个网站」
  「帮我分析这个 apk」「这个能不能打」「继续」）先归化成结构化、可执行的 CTF 提示词再执行。
  归化产物按 10 段输出：角色与任务类型 → 目标与范围 → 可验证的成功标准 → 已知上下文 →
  执行路线 → **工具绑定**（挂载本机全部已知工具）→ 证据要求 → 停止条件与红线 →
  **自检问题（决策点）** → 交付物。内含「Right Altitude」调档（清晰请求走轻量通道，
  不过度加工）、决策点自检、以及源自 Anthropic 实践与成熟 prompt 框架的模式库
  （references/04-prompt-patterns.md）。Use this skill at the START of any turn where the
  user gives a CTF/pentest/hack/reverse/malware/forensics request that is vague, terse,
  ambiguous, or missing scope/success-criteria — including single words like「继续」「看看」
  「打一下」, a bare URL, an IP, a file, or a dump — and whenever the user asks to
  "优化提示词"/"normalize prompt"/"把这个需求写清楚". Triggers even without the word "skill".
  Safety: never turns an out-of-scope or unauthorized target into an attack plan; routes
  such input to read-only recon, SRC reporting, or a local lab instead.
---

> 本文中的相对路径写法 `tools/xxx.py` 指**本机 CTF 工具目录中的脚本**（工具目录路径随机器而异；换机后按实际路径解析，找不到即标注缺失并给替代方案）。

> **⚠️ 三层分工（⌛2026-09-23 Owner 裁定，务必先读）** —— 本项目的"输入优化"由**三层**共同完成，
> **职责不同、不重叠**；**本 skill 只管其中一层**：
>
> | 层 | 落点 | 管什么 |
> |---|---|---|
> | **① 网关层** | `config/prompt_prefix.yaml` → 由本包 `llm_gateway.py` 注入 | **授权背景 + 输出形式**（"能不能做"）。**对走网关的所有程序生效，必过、跳不掉。** |
> | **② 本 skill** | 此处 | **把模糊输入归化成 10 段结构化任务规格**（"怎么说清楚"）。**由模型主动读取**，非强制注入。 |
> | **③ hook 层** | `.claude/hooks/ctf_normalize.py` | **CTF 项目上下文**（5 条纪律 + 8 个 skill 清单）。只对 Claude Code 生效。 |
>
> **⇒ 读到本 skill 时：不要重复输出授权声明**（① 已贴）；**不要重复列 skill 清单**（③ 已列）。
> **本 skill 的产出就是那 10 段结构本身。**

# CTF 提示词优化器 v2

**一句话**：把「人话」编译成「可执行的 CTF 任务规格 + 工具绑定 + 自检点」，再动手。

v2 相对 v1 的三处升级（均来自成熟方案调研，见 `references/04-prompt-patterns.md`）：
1. **Right Altitude 调档** —— 不一味加重结构；清晰请求只补缺口，避免把小任务加工成大工程。
2. **自检问题** —— 输出里带决策点，让执行前的判断显式化，减少「闷头做错方向」。
3. **模式库** —— 写提示词/写 skill 时可查 10 个成熟模式（角色、清单、少样本、边界、CoT…）。

## 0. 何时触发

| 输入形态 | 例子 | 归化强度 |
|---|---|---|
| 极简/含糊 | 「继续」「看看这个」「打一下」「这个行不行」 | **重构**：补全 10 段 |
| 半具体 | 「帮我分析这个 apk」「这个网站有漏洞吗」+ 附件/URL | **补全**：补缺口 |
| 已很具体 | 「用 SQLi 打 /admin 登录框，范围只有该 host」 | **直通 + 自检**：只核对范围/成功标准/停止条件 |

**Right Altitude 原则**（关键调档）：
- **太低（过度约束）**：把每步都写死 → 脆、限制推理、一线发现无法反馈。
- **太高（过空）**：只说「去看看吧」→ 无指导、行为不可预测。
- **刚好**：给出**边界与判据**，把**方法与顺序留给执行时判断**。
⇒ 归化的产物应当是「有约束力的规格」，不是「逐条命令脚本」。

**非 CTF 输入**：不要硬套框架。脚本类 → 做成 CTF 可复用工具；文档类 → 走报告规范；
完全无关 → 如实说明并按通用工程处理。

## 1. 归化流程（5 步）

```
① 摘意图   —— 用户到底要拿到什么？（shell / 结论 / 报告 / 一份数据 / 一个判断）
② 判类型   —— Web / 链上 / 逆向 / 移动 / 取证 / 密码 / 主机 / 杂项 / 学习
              并给模板族猜测（ctf-field-notes/references/01 + families/f01..f13）
③ 补缺口   —— 按 §2 的 10 段逐段检查：缺的补，推断的标「假设」并写验证方法
④ 挂工具   —— 按 §3 显式列出本任务要用的工具（含缺失能力的替代）
⑤ 输出执行 —— 先给「优化后的提示词」（或三行摘要），再按它做第一步
```

**输出后不要停下等确认**，除非：授权依据为「待确认」，或下一步是破坏性操作。

## 2. 优化后提示词的模板（10 段）

```markdown
### 优化后的提示词

**1. 角色与任务类型**
以<资深安全工程师 / 逆向分析师 / 链上研究员>视角；任务类型=<…>；模板族猜测=<…>
触发技能：ctf-playbook <章> → ctf-field-notes <references/族> → onchain-ctf（若涉链）

**2. 目标与范围**
目标：<域名/IP/文件/合约/附件>
授权依据：<用户声明 / 题面 / 自建 lab / **待确认**>
禁止项：<相邻主机、真实用户资产、未列明范围>

**3. 成功标准**（必须可验证，不能是"看看"）
例：产出资产表 + 至少一条 observed 发现 / 读到指定数据 / 明确判否并封板

**4. 已知上下文**（先查再写，避免重做）
- 记忆与 artifacts：<project-ctf-*.md 的相关条目 或 "无">
- 同族已打过的目标与结论：<06-case-index 条目 或 "无">

**5. 执行路线**
<按类型的阶段链>；先做：<低风险高信息量的一步>；后做：<需确认的步骤（标注）>

**6. 工具绑定**（详见 §3；留兜底句）
- 技能：… / 内置：… / 本机：… / 复用脚本：… / 记忆：…
- 兜底：所需工具先 `command -v`/`find` 实测存在；本机缺失能力显式标注并给替代

**7. 证据要求**
artifacts/<target>/…；每条含 来源+证据+复现+影响+范围确认；分级 confirmed/likely/unverified

**8. 停止条件与红线**
速率与配额 · 见 429/1015/461/锁定/告警即停 · 写操作需逐条确认 · 判否即封板 ·
**不许把「未授权真实目标」写成攻击计划**

**9. 自检问题（决策点）**
- 这是在授权范围内吗？（不确定 → 停下问）
- 我的成功标准可验证吗？（不可 → 重写）
- 这一步是只读还是写入？（写入 → 先列回滚清单）
- 我是不是在重复已做过的枚举？（是 → 先读记忆）
- 拿到这个结果，能支撑到哪一级证明？（只能 observed 就别写 confirmed）

**10. 交付物**
<报告结构 / 数据文件 / 脚本 / 复现步骤>
```

## 3. 工具绑定（优化后的提示词必须能调用全部已知工具）

**3.1 技能层**

| 场景 | 挂载 |
|---|---|
| 通用渗透（Web/主机/内网/取证/密码） | `ctf-playbook` + `ctf-field-notes` |
| 链上 / DApp / 资金盘 | `onchain-ctf` + `ctf-field-notes` |
| 判族 / 封板 / 上次怎么卡的 | `ctf-field-notes` |
| 写报告（Word/PDF/Excel/PPT） | `anthropic-skills:docx` / `pdf` / `xlsx` / `pptx` |
| 审自己写的 skill / 装第三方 skill 前 | `tools/skill_audit.py`（见 §3.3） |

**3.2 内置工具层**

`Bash` · `Read`/`Write`/`Edit` · `Glob`/`Grep` · `WebFetch`/`WebSearch` ·
`Agent`（`Explore`=并行只读侦察、`general-purpose`=多步、`Plan`=方案）·
`TaskCreate`/`TaskUpdate` · `Skill` · `NotebookEdit` · MCP（浏览器/终端）

**3.3 本机工具层**（详见 `ctf-field-notes/references/05-toolchain.md`）

```
python : <Python312 绝对路径>  （eth_account/eth_keys/eth_utils/androguard/requests/
         Crypto/dns/yaml 已装；**web3 未装→手写 JSON-RPC**）
二进制 : curl / openssl / nslookup / perl / git / rg / powershell   （**dig 缺失→nslookup**）
代理   : curl -x http://127.0.0.1:10809   （默认通道；直连常被干扰）
APK    : <项目根>/apk_analysis/tools/{axml.pl,apksig.pl,strx.pl,hermes-decomp.exe,...}
自研脚本: tools/{skill_audit.py, recon_replica.py} + artifacts 下各项目复用脚本
```

**3.4 记忆层**：`~/.claude/projects/.../memory/` 的 `project-ctf-*.md`（20 个目标）、
`onchain-broadcast-hygiene`、`skills-library`。**开工前先读相关档案**。

**3.5 兜底原则**：提示词里必须留一句「工具兜底」——
所需工具若不在清单内，先 `command -v`/`find` **实测存在**再启用；
本机没有的能力（Java/Node/.NET）**显式标注**并给 Python 替代方案。

## 4. 非 CTF 输入的归化规则

| 输入 | 归化为 |
|---|---|
| 「帮我写个脚本」 | **CTF 可复用工具**（放 `artifacts/<target>/scripts/` 或 `tools/`，带用法与占位符） |
| 「这份日志/流量/文件看看」 | 取证/杂项：走 ctf-playbook 09，产出解码与结论分级 |
| 「这个漏洞怎么修」 | 防守视角：检测/缓解/加固边界 |
| 「帮我写报告」 | 走 `docx`/`pdf`/`xlsx`，按报告规范 |
| 完全无关 | 如实说明不在 CTF 范围，按通用工程处理 |

## 5. 红线（不许做的事）

- **不许把未授权的真实生产目标优化成攻击计划** → 改道只读测绘 / SRC 报告 / 本地 lab。
- **不许把「取走真实用户资产」写成成功标准**。
- **不许省略停止条件**（无停止条件 = 未优化）。
- **不许把假设写成事实**（补全的段若为推断，标注并给验证方法）。
- **不许因为输入短就降低标准**（「继续」恰恰最需要完整归化）。
- **不许过度约束**（Right Altitude：给边界与判据，不写死每一步）。

## 6. 写提示词 / 写 skill 时的模式库

10 个成熟模式（角色 / 职责 / 清单 / 少样本 / 输出格式 / 边界 / CoT / 上下文约束 /
工作流 / 自检问题）及完整示例，见 **`references/04-prompt-patterns.md`**。
本 skill 自身的 10 段模板就是这套模式的 CTF 特化版。

## 7. 最小示例

**输入**：「这个站看看」+ `https://example-target.test`

```
1 角色类型：Web · 族待判 · 挂 ctf-playbook 01→02 + ctf-field-notes 01/families
2 目标范围：example-target.test；授权依据=用户声明（待确认）
3 成功标准：资产表 + 至少一条 observed 发现，或明确判否
4 上下文：查 06-case-index 有无同族；读相关 project-ctf-*.md
5 路线：被动优先（证书 SAN/DNS/前端 JS）→ 低风险指纹 → 再决定是否发请求
6 工具：Bash+curl(-x 代理)/openssl/nslookup · WebFetch · Grep 搜 JS · recon_replica.py
7 证据：artifacts/example-target/01-recon/{raw,notes}
8 停止条件：≥1s/请求；见 429/CF 即停；不爆破；写操作需确认
9 自检：授权成立吗？成功标准可验证吗？这步只读吗？
10 交付物：recon 小结 + 资产表
```
**执行**：授权待确认 ⇒ 只做不产生目标侧日志的被动动作，同时并行澄清。
