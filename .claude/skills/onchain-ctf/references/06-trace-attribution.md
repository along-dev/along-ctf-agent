# 06 资金追踪与归因

追踪资金流向、锁定相关地址。

## 追踪方法

1. 从目标地址查交易历史（Etherscan API / RPC `eth_getLogs`）。
2. 追踪 `Transfer` 事件，画资金流图。
3. 锁定收款方、混币/tornado 入口、CEX 充值地址。

## 归因产出

- 资金流向表（from → to → 金额 → tx hash）。
- 相关地址簇（同一手续费来源/同一归集地址）。
- 结论分级：直接关联 / 疑似关联 / 无关联。

## 工具

- Etherscan/Blockscout API、`eth_getLogs`、图数据库或 csv 手绘流向。
