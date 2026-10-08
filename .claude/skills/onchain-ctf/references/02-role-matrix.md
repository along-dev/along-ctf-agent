# 02 合约角色矩阵

用 eth_getCode 拿字节码，反汇编/找 ABI，枚举函数与访问控制。

## 枚举步骤

1. `eth_getCode` 拿字节码 → `cast disassemble` 或反编译工具找函数签名。
2. 找 ABI（Etherscan/Sourcify/题面附件）。
3. 建角色矩阵表：

| 函数 | 可见性 | 调用者约束 | 状态变更 | 风险 |
|---|---|---|---|---|
| withdraw | public | onlyOwner | 转出余额 | 高（若约束缺失） |
| mint | public | 无 | 增发 | 高 |
| transfer | public | 无 | 转账 | 中 |

## 判据

- `public/external` + 无 `onlyOwner`/无 `require(msg.sender==owner)` = 潜在抽干点。
- `onlyOwner` 存在但要审查 owner 转移逻辑（`transferOwnership` 是否可被任意调用）。
- 注意 `delegatecall` / 代理合约，真逻辑可能在实现合约。
