# 工具链速查（按用途分类）

本机已安装，直接调用。

## 侦察 / 测绘类

| 工具 | 用途 | 常用参数 |
|---|---|---|
| nmap | 端口 / 服务扫描 | `-sV -sC -T4 -p-` `-oA` |
| masscan | 全网段高速扫描 | `-p1-65535 --rate=1000` |
| subfinder | 子域枚举 | `-d <domain> -all` |
| httpx | 存活 / 指纹探测 | `-sc -title -tech-detect` |
| ffuf | 目录 / 参数 / 子域 fuzz | `-u <url>/FUZZ -w <wordlist> -fc 404` |
| dirsearch | 目录爆破 | `-u <url> -e php,asp,jsp` |

## Web 漏洞类

| 工具 | 用途 | 常用参数 |
|---|---|---|
| nuclei | 模板化漏洞扫描 | `-l <list> -t cves/ -severity critical,high` |
| sqlmap | SQL 注入 | `-u <url> --batch --dbs` / `-r req.txt --level=5 --risk=3` |

手动面：XSS、SSRF、SSTI、LFI、命令注入、反序列化、JWT、逻辑缺陷。
验证手法见 `killchain.md` 第 3 节。

## 内网 / 域渗透类

| 工具 | 用途 |
|---|---|
| impacket 套件 | psexec / wmiexec / smbexec / secretsdump / GetUserSPNs |
| msfconsole | 综合利用框架、模块化 payload |
| sliver | C2 框架，上线与后渗透 |

## 提权 / 凭证类

| 工具 | 用途 |
|---|---|
| hashcat | 哈希破解（`-m 1000` NTLM，`-m 1800` sha512crypt） |
| linpeas / winpeas | 提权信息枚举脚本 |

## 逆向 / CTF 类

| 工具 | 用途 |
|---|---|
| ghidra | 二进制反编译 / 静态分析 |
| frida | 动态插桩、脱壳、hook |

逆向方向：脱壳 → 加密算法识别 → patch / keygen / 激活绕过 / DRM 分析。
CTF 方向：Web / Pwn / Crypto / Re / Misc 分类速通。

## 情报类

- 多引擎联网搜索 + 网页抓取 + 正文净化。
- FOFA 资产测绘：先跑 `fofa.config` / `fofa.account` 自检凭据与额度，再 `fofa.search`。
- 威胁情报：IOC 检索、CVE / PoC 跟踪。

## 编排原则

- 侦察、测绘、扫描三个阶段的多个目标可并行。
- 漏洞验证阶段对单目标串行、对多目标并行。
- 每个工具产出统一落盘到工作目录，命名带阶段前缀（如 `01_recon_`、`02_scan_`）。
