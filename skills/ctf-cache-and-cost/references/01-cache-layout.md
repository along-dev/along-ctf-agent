# 01 缓存目录与键设计

## 目录

```
artifacts/<target>/
  cache/
    recon/          # 子域/指纹/目录结果
    chain/          # 合约字节码/ABI（按地址+区块号）
  notes/            # 人工判断
```

## 键设计

- 侦察缓存键 = `target + 时间窗`。
- 合约缓存键 = `address + block_number`。
- 判否结论键 = `family + 卡点`（存 case index，跨会话）。

## 命中判据

- 时间窗内 + target 一致 → 命中。
- 过期 → 重跑但 diff 增量（只补变化项）。
