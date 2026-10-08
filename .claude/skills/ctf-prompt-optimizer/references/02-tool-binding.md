# 02 工具绑定表（优化后的提示词必须能调用全部已知工具）

优化提示词的第 6 段必须**显式列出本任务要用的工具**，并留兜底句。
本文件是完整注册表；SKILL.md §3 是摘要。

> 原则：**先实测存在，再写进提示词**（`command -v` / `ls` / `find`）。
> 不得凭记忆假定某工具可用；本机没有的能力要显式标注替代方案。

## 1. 技能层

| 技能 | 何时挂 | 调用 |
|---|---|---|
| `ctf-playbook` | 通用 Web/主机/内网/取证/杂项 | Skill 工具，或按其 references 章节执行 |
| `ctf-field-notes` | **总是**（判族、卡点、封板、纪律、本机工具） | Skill 工具 |
| `onchain-ctf` | 涉及链上/密钥/合约/资金追踪 | Skill 工具 |
| `anthropic-skills:docx` / `pdf` / `xlsx` / `pptx` | 需要 Word/PDF/表格/幻灯片交付 | Skill 工具 |
| `dataviz` | 需要图表时可先读其配色/规格 | Skill 工具 |
| `update-config` | 需要改 settings.json / 钩子 / 权限 | Skill 工具 |
| `code-review` / `security-review` | 审自己写的 PoC / lab 代码 | Skill 工具 |
| `loop` | 需要周期性轮询/监控（如等窗口期） | Skill 工具 |

## 2. 内置工具层

| 工具 | 典型用途 |
|---|---|
| `Bash` | 主执行通道（curl/openssl/nslookup/perl/python/powershell） |
| `Read` / `Write` / `Edit` | 读证据、写脚本与报告、改配置 |
| `Glob` / `Grep` | 搜 artifacts、搜前端 JS、搜私钥语料 |
| `WebFetch` / `WebSearch` | 公开情报、文档、指纹查询 |
| `Agent` | `Explore`=并行只读侦察；`general-purpose`=多步任务；`Plan`=方案设计 |
| `TaskCreate`/`TaskUpdate` | 多阶段任务建清单 |
| `NotebookEdit` | 数据/分析型 notebook |
| MCP（浏览器/终端等） | 需要真实浏览器渲染或读终端时 |

## 3. 本机工具层（已实测核实 2026-09-13）

### 3.1 Python

```
python   (3.12.10 用户级)
```

| 模块 | 状态 | 用途 |
|---|---|---|
| `eth_account` `eth_keys` `eth_utils` | ✅ | 地址派生、EIP-191/EIP-712 签名、ecrecover |
| `requests` | ✅ | HTTP / JSON-RPC |
| `Crypto` (pycryptodome) | ✅ | AES/RC4/HMAC（协议还原） |
| `androguard` | ✅ | APK 静态分析 |
| `web3` | ❌ **未装** | **改用 `requests` 手写 `eth_call`/`eth_getCode`/`eth_getLogs`** |

**调用注意**：`python`(Store stub)/`py` 不可靠 → 用绝对路径；内联 `-c` 在 Git Bash 下可能
无输出 → **写成 .py 再跑**；`androguard` 开头加 `logger.remove()`；
子进程捕获加 `encoding="utf-8", errors="replace"`。

### 3.2 二进制

| 工具 | 状态 | 用途 |
|---|---|---|
| `curl` | ✅ | HTTP（境外目标加 `-x http://127.0.0.1:10809`） |
| `openssl` | ✅ | 证书 SAN、TLS 探测、编解码 |
| `nslookup` | ✅ | DNS |
| `dig` | ❌ | 用 `nslookup` 替代 |
| `perl` | ✅ | 自研解析脚本 |
| `git` / `rg` | ✅ | 代码/语料搜索 |
| `powershell` | ✅ | 跑 `portscan.ps1` / `quickprobe.ps1` |

### 3.3 APK / 移动逆向

```
<项目根>/apk_analysis/tools/
  axml.pl  apksig.pl  strx.pl  arsc1.pl  arsc_strings.pl  utf16_parity.pl
  hexdump.pl  chunks.pl  decode_strings.pl  hbc_head.pl  parse_ota.py  deep_dx.py
  hermes-decomp/hermes-decomp.exe   (v0.2.2, HBC 40–99)   hermes-mcp.exe
```

### 3.4 复用脚本（用 `find` 定位最新副本）

| 脚本 | 用途 |
|---|---|
| `keyderive.py` / `keyderive_scan.py` | ETH+TRON 私钥派生比对（含 pk=1..3 自测） |
| `credssp.py` | 纯 Python RDP NLA 凭据测试（⚠️ 严禁当爆破器，会锁死真实账户） |
| `tailaikey.py` | AES 加密 SQLite 私钥库解密 |
| `rce.py` / `sqlr.py` | MSSQL 堆叠注入 RCE / osql 回读 |
| `fe_crawl.py` | 前端 JS 抓取与端点提取 |
| `drain_exec.py` / `owner_drain_exec.py` | 链上提取执行器（先 `eth_call` 模拟再广播） |
| `emuc.py` / `tx.py` / `sandbox_*.py` | 本地 EVM 干跑 / state-override 沙箱 |
| `lulu_client.py` | 自研加密信封协议客户端 |
| `druid_pull.py` | Druid SQL 监控拉取（表结构情报） |
| `portscan.ps1` / `quickprobe.ps1` | PowerShell 并发端口扫描 |
| `_bakscan.py` | 私钥语料批量派生比对（目标地址表驱动） |
| `xdaoscan.py` | 轻量 Web 测绘（不登录不爆破） |

### 3.5 网络

```
代理(默认) : curl -x http://127.0.0.1:10809 ...      # 最稳定
直连       : 可能被劫持/丢弃（大陆家宽）；数据中心代理可能 TLS 黑洞
```

## 4. 记忆层

| 路径 | 内容 |
|---|---|
| `~/.claude/projects/.../memory/MEMORY.md` | 索引 |
| `project-ctf-*.md`（19 个） | 各目标结论、证据路径、恢复条件 |
| `onchain-broadcast-hygiene.md` | 广播卫生铁律 |
| `no-jvm-python-android-tools.md` | 工具链细节 |
| `skills-library.md` | 技能库约定 |

**开工前先读相关档案**——这是避免重做枚举的最大杠杆。

## 5. 不可用能力的替代表

| 想要 | 本机没有 | 替代方案 |
|---|---|---|
| Java 工具（jadx、apktool、Burp） | Java | 用 `apk_analysis/tools` 的 perl 脚本 + androguard；或问用户安装 |
| Node 工具（前端打包、部分 fuzz） | Node | 用 Bash + Python 静态提取 JS |
| `.NET` 反编译（ILSpy/dnSpy） | .NET 运行环境 | 用 Python 做 `#US` 堆/常量提取与偏移定位 |
| `web3.py` | 未装 | 手写 JSON-RPC（`requests` + `eth_account`） |
| `dig` | 缺 | `nslookup` |
| FreeRDP / rdesktop | 缺 | `credssp.py`（纯 Python NLA） |

## 6. 提示词第 6 段的写法（模板）

```markdown
**6. 工具绑定**
- 技能：ctf-playbook(01→02→03) · ctf-field-notes(01 族表 / 02 卡点) · onchain-ctf(若涉及链上)
- 内置：Bash · Read/Write/Edit · Grep/Glob · WebFetch · Agent(Explore)
- 本机：python=<绝对路径> · curl -x http://127.0.0.1:10809 · openssl · nslookup
- 脚本：<按需点名，如 fe_crawl.py 提取端点 / emuc.py 干跑>
- 记忆：先读 project-ctf-<同族>.md 与 06-case-index
- 兜底：所需工具若不在上表，先 `command -v`/`find` 实测存在再启用；本机没有的（Java/Node/.NET）
  显式标注并给 Python 替代
```
