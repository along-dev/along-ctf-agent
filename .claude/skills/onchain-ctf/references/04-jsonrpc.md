# 04 手写 JSON-RPC（无 web3）

本机无 web3，用 Python requests / curl 直接发 RPC。

## 核心方法

```python
import requests
RPC = "<RPC_ENDPOINT>"

def rpc(method, params):
    r = requests.post(RPC, json={"jsonrpc":"2.0","id":1,"method":method,"params":params}, timeout=15)
    return r.json().get("result")

# 只读四件套
code = rpc("eth_getCode", ["0xADDR", "latest"])          # 字节码
bal  = rpc("eth_getBalance", ["0xADDR", "latest"])        # 余额(wei)
slot = rpc("eth_getStorageAt", ["0xADDR", "0x0", "latest"]) # 存储槽
out  = rpc("eth_call", [{"to":"0xADDR","data":"0xSEL..."}, "latest"]) # 静态模拟
```

## 构造 calldata

- 函数选择器 = `keccak256("transfer(address,uint256)")[:4]`，参数各补 32 字节 ABI 编码。
- 用 `eth_utils` / `eth_account` 的编码能力，或手写。

## 停止条件

- 公共 RPC 有限流 → 分批 + 退避，见 429 即 `time.sleep` 重试，连续 3 次即停。
- 只读方法无副作用，可安全重试；广播方法绝不通过本流程自动发。
