---
name: ctf-playbook
description: >-
  Authorized CTF / penetration-testing playbook that turns a target or challenge
  into an evidence-backed workflow with 9 core phases and 3 focused chapters:
  scoped Shodan/FOFA discovery and TG Bot panel authentication audits, path
  traversal and avatar-upload validation, and attack-path planning. Use for
  authorized target enumeration, CTF challenges, vulnerability verification,
  shell or privilege-escalation tasks, and penetration-test planning or review.
  Route only to relevant chapters; distinguish proven capabilities from
  hypotheses and define scope, evidence, stop conditions, and cleanup.
---

# CTF / 渗透 实战 Playbook

把「一个目标或一道题」变成一条**有证据、可复现、低风险优先**的攻击链。核心不是背工具，而是：
**先授权 → 先摸清 → 先低风险验证 → 分级证明 → 留证据 → 清理**。

## 0. 铁律（先读这 7 条，再动手）

1. **授权先行**：只对用户明确授权的目标（`HOST` / `IP` / `CIDR` / 题目附件）执行。开始前确认并记录范围，含「禁止触碰」项。发现目标疑似在授权范围之外，停下确认，不擅自扩大。
2. **低风险优先**：先指纹/版本/配置，再无害验证，最后才到会写文件、命令执行、反连、爆破这类破坏性动作。能不用 EXP 就不用 EXP。
3. **分级证明，不许跳级**：结论用 `hypothesis`(猜测) / `observed`(有观察证据) / `primitive`(证明具体能力)；验证环境另记 `local_proof`(本地复现) / `remote_proof`(授权远端验证) / `not_tested`。本地复现不证明远端存在，不同能力不是固定升级阶梯。报告只能陈述证据支持的能力，把「DNSlog 回连」写成「拿到 shell」是禁止的。
4. **工具诚实**：找不到可靠官方来源的工具标「待核验」，不硬编功能。所有示例命令用占位符 `HOST` `TARGET` `TOKEN` `PAYLOAD`，不写真实密钥/目标。
5. **证据链**：每个发现至少含 `来源` + `证据(截图/原始响应/输出)` + `可复现方式` + `风险解释` + `范围确认`。落地到 `artifacts/` 目录。
6. **防守视角**：每次攻击动作，同时回答「防守方在日志/进程/网络里会看到什么」。这对 CTF 复盘和真实报告都值钱。
7. **清理**：复现后删除测试文件、临时账号、临时监听；记录影响面。

## 1. 启动：先分类，再调度

拿到任务先判断它属于哪类，再决定走哪几章（共 12 章，不要求按序跑完）：

| 挑战类型 | 特征 | 走哪些章 |
|---|---|---|
| Web 题 | URL、登录、SQLi、上传、路径穿越、反序列化、CMS | 01 → 02 → 03（→ 04 如遇 WAF；上传/穿越走 11） |
| 内网/主机渗透 | 给了内网 IP、Windows/Linux 靶机 | 01 → 02 → 05 → 06 → 07 → 08 |
| 测绘/后台审计 | 授权域名或 IP/CIDR、后台暴露、Bot 面板 | 01 → 10；涉及认证测试时先联读 06 |
| 逆向/Pwn | 二进制、固件 | 09(反编译/取证) + 逆向工具 |
| 杂项(Misc) | 隐写、编码、流量包、内存镜像 | 09（编码/哈希/加密/流量包） |
| 取证(Forensics) | 磁盘/内存/日志 | 09 + 证据归档方法 |
| 密码学(Crypto) | 密文、加密题 | 09（编码/哈希/加密区分） |

对不明确的题，先花一小段做**分类侦察**：读题面、看给了什么文件/URL/端口，再确定主攻路线。

> **第 12 章贯穿各阶段**：已有多个线索、不知道下一步、连续验证无进展或准备复盘时，读取 [第 12 章](references/12-attack-chain-thinking.md)，用事实、假设、实验和反馈记录决策。

## 2. 九阶段调度表 + 3 个横向章（详细步骤在 references/ 里按需读取）

每个阶段的 reference 文件都按「目标 → 检查清单 → 工具 → 证据模板 → 常见误区 → 防守视角」组织。**读一个阶段前先读它的 reference**，不要凭印象做。

| 阶段 | reference | 一句话目标 |
|---|---|---|
| 01 信息收集 | `references/01-recon.md` | 画出目标所有门：资产/子域/端口/前端 API/目录 |
| 02 漏洞扫描 | `references/02-scan.md` | 搞清门后是什么锁、锁有没有已知问题 |
| 03 漏洞利用 | `references/03-exploit.md` | 授权内最小影响地证明锁真的坏，并拿证据 |
| 04 免杀/绕过 | `references/04-evasion.md` | 遇到 WAF/杀软时的对抗与防守检测 |
| 05 隧道/代理 | `references/05-tunnel.md` | 内网服务不暴露时的转发通道 |
| 06 爆破/账号 | `references/06-credential.md` | 弱口令审计，控制速率和停止条件 |
| 07 本地提权 | `references/07-privesc.md` | 低权限升高权限，先查配置再查 CVE |
| 08 横向/后渗透 | `references/08-lateral.md` | 凭证抓取、横向移动、持久化 |
| 09 辅助/取证 | `references/09-tools.md` | 编码/哈希/加密区分、反编译、格式化、归档 |
| **10 测绘与 Bot 后台审计** | [references/10-cyberspace-mapping.md](references/10-cyberspace-mapping.md) | 范围约束查询 → 候选归属 → 登录基线 → 有预算的认证审计 |
| **11 路径穿越/上传** | [references/11-path-traversal.md](references/11-path-traversal.md) | 明确后端数据流，用受控文件区分读取、写入、越权与执行 |
| **12 证据驱动决策** | [references/12-attack-chain-thinking.md](references/12-attack-chain-thinking.md) | 线索 → 可证伪假设 → 最小实验 → 反馈门 → 继续/换路/收尾 |

**调度规则**：按上表的挑战类型选阶段，串成一条链执行；每完成一阶段就产出该阶段的证据文件，作为下一阶段的输入（例如 01 产出的资产表喂给 02 的扫描）。
第 **10–12 章为补充/横向章**：10 深化 01 的测绘分支，认证预算沿用 06；11 深化 03 的文件处理分支；12 负责跨阶段决策，不要求做完后渗透再读取。只加载当前分支需要的参考资料。

资料编辑、语法讲解和离线案例分析不等于启动目标测试，也不会自动开启 red-team 模式。继承会话已有授权，不重复询问已明确事项。项目存在自动化执行框架时，动作必须通过其 Tool Registry、Scope Gate、Executor adapter；缺少工具或范围时明确记录未执行。

## 3. 贯穿全程的「证据与证明」规范

### 3.1 证据目录结构

```
artifacts/
  01-recon/   raw/ img/ tables/ notes/
  02-scan/    raw/ fingerprints.csv manual-review.md
  03-exploit/ raw/ img/ notes/proof-chain.md
  ...
  09-tools/   raw/ decoded/ scripts/ notes/
  10-mapping/ raw/ hits.csv notes/ in-scope-vs-out.md
  11-path-traversal/ raw/ notes/test-matrix.md notes/cleanup.md
  12-reasoning/ hypotheses.md decision-log.md chain.md
```

原始证据放 `raw/`，截图放 `img/`，结论表放 `tables/` 或 `.csv`，人工判断放 `notes/`。临时文件放 `cache/`，别把缓存当证据。

### 3.2 资产表最小字段

```
asset, type, ip, port, protocol, title/fingerprint, source, status, evidence
```

状态用：`candidate`(未验证) / `observed`(已验证) / `negated`(验证无效) / `interesting`(值得深入)。

### 3.3 发现记录的补充字段

每个发现分别记录 `finding_id, asset, scope_ref, evidence_ids, claim_level, validation_context, capability, prerequisites, status, next_action, stop_condition, cleanup`。证明级别与验证环境使用第 0 节定义；调查状态用 open/confirmed/negated/blocked/deferred，blocked 不表示漏洞不存在。模板与示例见第 12 章。

### 3.4 报告模板（完成目标测试或复盘时产出）

```markdown
# 目标小结：TARGET
## 执行摘要（一句话攻击面 + 已证明到哪一级）
## 时间线（每步：动作 → 命令 → 观察 → 结论级别）
## 发现清单（每条：入口/请求/响应/影响/证据路径/证明级别）
## 防守视角（这些动作在日志/EDR/网络里会留下什么）
## 清理与影响（删了什么、还原了什么）
## 未完成项（缺少哪些前提、哪些能力未验证、下一步由谁处理）
```

## 4. 写作与用词的硬性规范

- 写「**Base64 编码**」，不写「Base64 加密」；写「**MD5 哈希匹配到候选原文**」，不写「解密 MD5」。
- 写「**版本线索指向受影响范围，仍需确认补丁状态**」，不写「工具报了 Struts2，已确认漏洞」。
- 看到疑似加密的数据，先找算法/密钥/IV 来源证据，不要看到乱码就说 AES。
- 反编译结果写「**反编译观察到**」，不当「源码原文」。

## 5. 遇到卡点怎么办

- **不确定目标是否授权** → 停下问，不猜。
- **工具没有可靠来源** → 标「待核验」，用通用方法替代（例如目录扫描用 dirsearch 的通用思路）。
- **扫描报高危但拿不到证据** → 回到证明分级，只写「observed」，不写「存在漏洞」。
- **需要爆破** → 先写速率/停止条件/测试账号边界，再执行；命中即停。
- **测绘命中 bot_token 或面板标题** → 读 10，核对归属、采集时间与模板误报，不能据此确认泄露或弱口令。
- **上传成功但落点未知** → 读 11，区分回显、公开映射与真实写入，不靠猜目录层数继续覆盖。
- **多个线索不知如何推进** → 读 12，明确前提、反馈门与出口，选择一个可证伪实验。
