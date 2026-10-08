# 05 本机工具能力与缺失替代

开工前**先实测存在**（`command -v` / `find`），不假设装了。

## 已装（本机）

```
python3 : eth_account / eth_keys / eth_utils / androguard / requests / Crypto / dns / yaml
二进制  : curl / openssl / nslookup / perl / rg / powershell
代理    : curl -x <PROXY_URL>   （默认通道；直连常被干扰，URL 以环境变量为准）
APK     : apk_analysis/tools/{axml.pl, apksig.pl, strx.pl, hermes-decomp.exe}
```

## 缺失（显式标注 + 替代）

| 缺 | 替代 |
|---|---|
| web3 | 手写 JSON-RPC（eth_call/eth_getCode 等） |
| dig | nslookup |
| Java | 反编译改用 Python 工具或标注缺失 |
| Node | 前端打包分析改用 grep/正则 |
| .NET | 标注缺失，给静态分析替代 |

## 兜底原则

所需工具不在清单内 → 先实测存在再启用；没有的能力显式标注并给 Python 替代，不硬编功能。
