# 09 辅助工具 & 解密取证 & 资源库

**目标**：工具箱。判断数据是编码/哈希/加密，反编译看逻辑，格式化，归档证据。

## 三个概念必须分清

| 概念 | 是否需要密钥 | 能否还原 | 例子 |
|---|---|:---:|---|
| 编码 | 否 | 能 | Base64、URL 编码、Hex |
| 哈希 | 否 | 通常不能 | SHA-256、MD5 |
| 加密 | 是 | 有密钥才能 | AES、RSA |

## 检查清单

1. **识别数据**：看字符集特征判断类型（Base64 = A-Za-z0-9+/=；URL = %xx；Hex = 0-9a-f）。`eyJ...` 可能是 Base64URL 的 JSON，要验证。
2. **解码流程**：保留原始输入 → 记录 recipe（如 From Base64 → Gunzip → Decode UTF-8）→ 输出到 decoded/ → 写结论。
3. **哈希**：只能"匹配到候选原文"，不能"解密"。
4. **AES 分析**：先找算法/密钥来源/模式/IV/padding/认证标签/外层编码证据，别看到乱码就说 AES。
5. **Java 反编译**：jd-gui（JD-GUI）看 `.class/.jar`，关注 `application.yml`、Controller/Route、Filter/Interceptor、Service、Mapper/SQL、hardcoded secrets。写"反编译观察到"，不当源码原文。
6. **JSON/JWT**：JSON 用双引号、对象 `{}`、数组 `[]`；JWT 三段(header/payload/signature)，能解码≠能伪造，验证签名与算法。
7. **归档**：raw(原始证据)/decoded(结果)/img(截图)/scripts(可复现脚本)/notes(判断)；Lib(依赖)和 cache(临时)不当证据。

## 工具（可核验来源）
JD-GUI、CyberChef（通用编码/加密/压缩，GCHQ）。待核验：jiamijiemi、auxtools、cx、0x7eTeamTools。

## 证据模板（数据识别）
```markdown
## 数据识别
- 原始长度 LEN；字符集特征(疑似 Base64)
- 标准依据 RFC 4648
- 解码工具 CyberChef / python base64
- 结果 得到 JSON，对照 RFC 8259 可解析
- 结论 observed
```

## 相关 RFC（用词依据）
JSON=RFC 8259；Base64=RFC 4648；URI=RFC 3986；JWT=RFC 7519；AES=NIST FIPS 197。

## 快速检查清单
[ ] 分清编码/哈希/加密  [ ] 保留原始输入  [ ] 记录工具版本和步骤  [ ] 没写真实密钥  [ ] 用 RFC/官方文档支撑  [ ] 临时文件放 cache、证据放 raw/decoded  [ ] 敏感值脱敏。

## 常见误区
Base64 叫加密｜MD5 叫解密｜乱码就说 AES｜反编译结果当源码｜cache 当证据｜工具结果不写步骤。
