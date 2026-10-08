# 03 抽干路径枚举

抽干 = 让合约资产以非预期方式流出。

## 典型路径

| 路径 | 特征 | 验证 |
|---|---|---|
| public withdraw 无鉴权 | 任意人可提 | eth_call 模拟 |
| mint 无限增发 + 兑换 | 通胀抽干 | 模拟 mint→swap |
| 重入（reentrancy） | 外部调用在状态更新前 | eth_call + 源码审计 |
| 代理升级点未锁 | 可替换实现合约 | 查 admin/upgradeTo |
| 授权无限（approve 漏洞） | 用户误授 token | 链上查 allowance |

## 验证分级

- 存在源码 → 静态审访问控制 → `hypothesis` 定级。
- 无源码 → 反汇编看 selector → `eth_call` 模拟 → `observed`。
- 模拟确认资产可流出 → `primitive`（只读证明，不真广播）。

## 红线

- "抽干"只针对用户自有/题面授权/测试网合约。
- 公共主网真实第三方资产：不写成成功标准，转只读测绘或 SRC 报告。
