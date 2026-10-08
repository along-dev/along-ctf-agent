---
name: onchain-ctf
description: >-
  链上 / DApp / 智能合约 CTF 专项。把"合约能不能抽干""这个地址能不能动"这类问题归化
  成一条只读优先的证据链：密钥材料识别 → 合约角色矩阵 → 抽干路径枚举 → 只读模拟
  （eth_call）→ 广播卫生 → 追踪归因。全程默认只读、不广播，广播需用户逐项确认。
  当任务涉及合约地址、私钥材料、DApp、资金盘、代币、DeFi、链上资产时使用。触发词：
  合约、链上、抽干、代币、DeFi、eth_call、私钥、助记词、资金盘、RPC、钱包、地址余额。
---

# 链上 CTF 专项 · onchain-ctf

> 定位：这是 `ctf-playbook` 的**链上分支**，只负责链上攻击面。
> 铁律：**默认只读（`eth_getCode` / `eth_call` / `eth_getStorageAt`），不广播交易**；
> 广播（`eth_sendRawTransaction`）需用户逐项确认，且只对用户自有的私钥/合约。

## 0. 六步证据链（按序，可跳过无关键材的步骤）

| 步 | 要回答 | 读哪个文件 |
|---|---|---|
| 1 密钥材料识别 | 有没有私钥/助记词/签名权？ | `references/01-key-material.md` |
| 2 合约角色矩阵 | 谁有 mint/withdraw/owner 权？ | `references/02-role-matrix.md` |
| 3 抽干路径枚举 | 有没有 public 无权限的提现/转账路径？ | `references/03-drain-path.md` |
| 4 只读模拟 | 用 eth_call 静态验证，不广播 | `references/04-jsonrpc.md` |
| 5 广播卫生 | 真要发交易时的防误伤纪律 | `references/05-broadcast-hygiene.md` |
| 6 追踪归因 | 资金去哪了 / 谁在动 | `references/06-trace-attribution.md` |

## 1. 本机能力边界（先看，别假设有 web3）

- **已装**：`eth_account` / `eth_keys` / `eth_utils`（可离线生成地址、签交易、算 keccak）。
- **未装**：`web3` —— 一律**手写 JSON-RPC**（见 `references/04-jsonrpc.md`），用 `curl` / Python `requests` 直接发 RPC。
- **RPC 端点**：公共 RPC 有限流，需分批退避（见停止条件）。

## 2. 成功标准（必须可验证）

链上任务的成功标准**不能是"能不能抽干"这种不可验证表述**，改写为：

- 产出**合约角色矩阵**（函数 × 权限 × 调用者约束），标注每个函数的访问控制。
- 结论分级：`public 无权限提现路径存在`（primitive）/ `疑似存在，待模拟`（observed）/ `判否`（negated）。
- 只读模拟的证据：`eth_call` 的原始响应 + 解码结果。

## 3. 授权与广播红线

- **只读**（`eth_call` / `eth_getCode` / `eth_getStorageAt` / `eth_getBalance`）对公共链无副作用，可直接做。
- **广播**（`eth_sendRawTransaction`）是**写操作**，逐条列回滚清单，需用户确认目标合约与金额。
- **不许把"取走真实第三方用户资产"写成成功标准**——链上 CTF 的"抽干"只针对用户自有合约 / 已给题面授权合约 / 本地测试网。

## 4. 最小示例

**输入**：这个合约能不能抽干 `0x1234...abcd`

```
1 密钥材料：无（先确认用户是否持有可签名地址）
2 角色矩阵：eth_getCode 拿字节码 → 反汇编/找 ABI → 枚举 owner/mint/withdraw/transfer
3 抽干路径：重点看 withdraw/claim 是否 onlyOwner，有没有 public 可调且未校验的路径
4 只读模拟：用 eth_call 模拟 withdraw(巨额)，看是否 revert / 余额是否变化
5 广播：先列回滚清单，金额与目标合约逐项确认，公共主网默认不广播
6 归因：若目标是被盗/资金盘，追资金流向、锁定套利地址
```

## 参考文档

- `references/01-key-material.md` — 私钥/助记词/签名权识别与离线工具
- `references/02-role-matrix.md` — 合约角色与访问控制枚举
- `references/03-drain-path.md` — 抽干路径枚举与判据
- `references/04-jsonrpc.md` — 手写 JSON-RPC（无 web3）
- `references/05-broadcast-hygiene.md` — 广播纪律与回滚清单
- `references/06-trace-attribution.md` — 资金追踪与归因
