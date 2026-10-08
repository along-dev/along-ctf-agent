---
name: ctf-field-notes
description: >-
  CTF / 渗透「族·卡点·封板判据」笔记库（战地笔记）。负责三件事：①把新目标判到
  模板族（f01..f13），命中同族既有结论，避免从零重新枚举；②把"卡住/没进展"对号到
  已知卡点与解法；③给出封板判据（什么时候判定"这个方向已死"并停止）。在 ctf-playbook
  进入 01 侦察之前、判族/查同族结论/决定封板/复盘"上次怎么卡的"时使用。触发词：判族、
  族、卡点、封板、没进展、卡住、上次怎么、这个族、案例、复盘。
---

# CTF 战地笔记 · 族 / 卡点 / 封板判据

> 定位：这是**记忆层 + 决策层**，不是流程层。流程交给 `ctf-playbook`，归化交给
> `ctf-prompt-optimizer`，本技能只回答三个问题：
> **这是哪个族？上次怎么卡的？什么时候该收手（封板）？**

## 0. 三件事（每件事对应一个 reference）

| 要回答的问题 | 读哪个文件 | 产出 |
|---|---|---|
| 这是哪个族 / 同族结论 | `references/01-family-taxonomy.md` | 族号 + 命中同族案例 |
| 卡住了 / 没进展 | `references/02-stuck-points.md` | 卡点对号 + 解法 |
| 该不该封板 | `references/03-closure-criteria.md` | 封板判据 + 封板动作 |
| 有没有同类先例 | `references/04-case-index.md` | 案例索引（先查再写） |
| 本机工具能力 | `references/05-toolchain.md` | 工具清单 + 缺失替代 |

**使用顺序**：判族 → 查案例 → 若卡住对号卡点 → 若无进展看封板判据。

## 1. 判族（f01..f13）

新目标先花一小段做**分类侦察**（读题面、看给了什么文件/URL/端口/合约），
再到 `references/01-family-taxonomy.md` 查族表。族号不是唯一——一个目标可能叠加多个族
（例如"Web 后台 + 链上资产"= f02 + f08），**主族决定主攻路线，副族决定并行侦察**。

判族时先回答三个问题：
1. 给了什么载体？（URL / IP / 附件 / APK / 合约地址 / 密文 / 流量包 / 内存镜像）
2. 目标边界在哪？（单个服务 / 内网段 / 单合约 / 单文件）
3. 预期产出是什么？（shell / flag / 结论 / 报告）

## 2. 卡点对号

连续 2-3 次验证无进展时，不要继续闷头试，转到 `references/02-stuck-points.md`
按「卡点症状」对号。典型卡点：

- **有 404/无响应** → 可能框架统一 404、WAF、范围错、协议错。
- **有告警/封 IP** → 停止条件触发，转被动或封板。
- **能读不能写** → 权限边界，先判"读取"和"写入"是两条不同链。
- **能写不能执行** → 缺执行原语，回到上传/包含/反序列化找执行点。
- **本地能复现远端不行** → `local_proof` ≠ `remote_proof`，别把本地结论外推。

## 3. 封板判据（硬规则）

**封板 = 判定"当前方向已死"并记录，不是放弃任务，而是切换路线或收敛结论。**
满足任一即封板（详见 `references/03-closure-criteria.md`）：

1. 已覆盖该族全部已知弱点，全部判否（negated）。
2. 触发停止条件（429/1015/461/锁定/告警）且无法换源继续。
3. 结论已足够支撑"判否"或"已到证明上限"，继续加成本无信息增益。
4. 目标明确在授权范围外（转只读/封板 + 记录）。

封板后必须写 `references/04-case-index.md` 的一条案例，否则下次重做。

## 4. 证据与记录规范

- 每条发现最少字段：`finding_id, asset, claim_level(hypothesis/observed/primitive), validation_context(local_proof/remote_proof/not_tested), status(open/confirmed/negated/blocked/deferred), next_action`。
- 封板记录字段：`case_id, family, target, why_closed, evidence, what_to_try_next`。
- `blocked` 只表示"当前无手段"，**不等于"漏洞不存在"**，报告措辞必须区分。

## 5. 最小示例

**输入**：Web 站，有登录框，试了 SQLi 无回显，不知道下一步。

```
1 判族：f02（Web 登录/认证），叠加 f05（注入面待定）
2 查案例：04-case-index 查 f02 同族——有无"登录框 SQLi 无回显"先例
3 卡点对号：02-stuck-points 里"有框但无回显"→ 换盲注/时间盲注/报错注入，或先判后端
4 封板判据：若三种注入通道全判否 → 封板该方向，转认证模型审计（弱口令/默认凭据）
```

## 参考文档

- `references/01-family-taxonomy.md` — 13 族分类 + 每族主攻路线
- `references/02-stuck-points.md` — 卡点症状 → 解法
- `references/03-closure-criteria.md` — 封板判据 + 封板动作
- `references/04-case-index.md` — 案例索引（查同族先例）
- `references/05-toolchain.md` — 本机工具能力 + 缺失替代
