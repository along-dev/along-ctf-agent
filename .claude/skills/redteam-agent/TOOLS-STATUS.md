# TOOLS-STATUS.md — 工具链核实与安装清单

> **核实时间**：2026-10-08
> **核实方法**：Windows PATH + WSL Ubuntu PATH + 常见安装目录 + 各包管理器，全部实探。
> **结论**：Windows 与 WSL **两侧的渗透工具链基本为空**，仅有少量 Python 侧能力可用。
> CLAUDE.md 中「工具链本机全装好了」的表述与实际不符，以本文为准。

## 一、当前已装（可直接用）

| 工具 | 位置 | 用途 |
|---|---|---|
| frida / frida-tools 17.x | Windows `/e/python-3.13/Scripts/` | 动态插桩、脱壳、hook |
| androguard / apkInspector | Windows Python | Android APK 分析 |
| ddddocr | Windows Python | 验证码识别 |
| pwntools 生态（`inv`/`asm` 相关） | 待确认 | Pwn/CTF（Python 包级） |
| pycryptodome / pycryptodomex | Windows Python | 加解密（Crypto 用） |
| requests / lxml / bs4 类 | Windows Python | HTTP 编排、正文解析 |
| paramiko | Windows Python | SSH 操作 |
| curl / wget | Windows + WSL 都有 | HTTP 抓取 |
| python3 | Windows + WSL | 脚本执行 |
| go 1.27.0 | Windows `/c/Program Files/Go/bin/go` | 编译安装 PD 全家桶 |
| docker | Windows（含多镜像） | 容器化靶场 / 隔离运行 |
| WSL Ubuntu 24.04 | 运行中 | Linux 侧工具宿主 |

**可直接干**：逆向/脱壳（frida）、APK 分析、Python 脚本、容器编排。
**不能直接干**：端口扫描、子域测绘、Web 漏洞扫描、SQL 注入、C2、内网、哈希破解（工具全缺）。

## 二、缺失工具链（按优先级）

优先级：**P0 核心扫描** > **P1 利用** > **P2 后渗透/内网** > **P3 逆向/专项**。

### P0 — 核心侦察扫描链（先装这批）

| 工具 | 用途 | 安装通道 |
|---|---|---|
| nmap | 端口/服务扫描 | winget / choco / WSL apt |
| subfinder | 子域枚举 | go install（PD） |
| httpx | 存活探测+指纹 | go install（PD，注意与 Python httpx 库同名） |
| nuclei | 模板化漏洞扫描 | go install（PD） |
| naabu | 高速端口扫描（PD 系） | go install（PD） |
| dnsx | DNS 探测（PD 系） | go install（PD） |
| katana | 爬虫（PD 系） | go install（PD） |

### P1 — 漏洞利用链

| 工具 | 用途 | 安装通道 |
|---|---|---|
| ffuf | 目录/参数 fuzz | go install |
| dirsearch | 目录爆破 | pip 或 git |
| gobuster | 目录/子域爆破 | go install |
| sqlmap | SQL 注入 | pip / git / WSL apt |
| wpscan | WordPress 扫描 | gem / WSL |
| nikto | Web 服务器扫描 | WSL apt / git |
| whatweb | Web 指纹 | WSL apt / gem |
| wfuzz | Web fuzz | pip |

### P2 — 后渗透 / 内网 / 域

| 工具 | 用途 | 安装通道 |
|---|---|---|
| impacket 套件 | psexec/wmiexec/secretsdump | pip（`impacket`） |
| hashcat | 哈希破解 | winget / WSL apt |
| john | 密码破解 | WSL apt |
| sliver | C2 框架 | go install / release |
| metasploit（msfconsole/msfvenom） | 综合框架 | WSL 官方安装脚本 |
| netexec (nxc) | 内网横向 | pip（`netexec`） |
| responder | 中间人/LLMNR 投毒 | git / WSL |
| certipy | AD CS 攻击 | pip（`certipy-ad`） |
| bloodhound-python | 域信息收集 | pip |
| evil-winrm | WinRM 利用 | gem / WSL |
| proxychains | 代理链 | WSL apt |

### P3 — 逆向 / 情报 / 专项

| 工具 | 用途 | 安装通道 |
|---|---|---|
| ghidra | 反编译 | 官网 release（需 JDK） |
| radare2 / rizin | 逆向框架 | WSL apt / git |
| binwalk | 固件/文件分析 | WSL apt / pip |
| gau / waybackurls | 历史 URL 收集 | go install |
| amass | 资产测绘 | go install（PD） |

---

## 三、安装命令（可直接执行）

### 通道 A：Go 装 ProjectDiscovery 全家桶（最快，go 已就绪）

```bash
# 设置 GOPATH/bin 到 PATH（Windows Git Bash 下）
export PATH="$PATH:$HOME/go/bin"

go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install -v github.com/projectdiscovery/katana/cmd/katana@latest
go install -v github.com/ffuf/ffuf/v2@latest
go install -v github.com/OJ/gobuster/v3@latest
go install -v github.com/lc/gau/v2/cmd/gau@latest
go install -v github.com/tomnomnom/waybackurls@latest
```

> 装完把 `%USERPROFILE%\go\bin` 加进系统 PATH（Windows），或在 Git Bash 里 `export PATH`。

### 通道 B：Python 包（pip 已就绪）

```bash
pip install sqlmap
pip install impacket
pip install netexec
pip install certipy-ad
pip install bloodhound
pip install dirsearch
pip install wfuzz
pip install pwntools
```

### 通道 C：Windows 原生（winget 已就绪）

```bash
winget install Insecure.Nmap
winget install hashcat.hashcat
winget install BurntSushi.ripgrep.MSVC   # 可选
```

### 通道 D：WSL Ubuntu（apt 已就绪，Kali 工具最全）

```bash
wsl -d Ubuntu -e bash -lc '
sudo apt update
sudo apt install -y nmap masscan sqlmap nikto whatweb wfuzz gobuster \
  john hashcat proxychains4 binwalk dirb wpscan
'
# Metasploit 官方脚本
wsl -d Ubuntu -e bash -lc 'curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > /tmp/msfinstall && chmod +x /tmp/msfinstall && sudo /tmp/msfinstall'
```

### 通道 E：GitHub Release（ghidra / sliver 等需下包的）

```bash
# ghidra: 下载 release zip 解压，配置 JAVA_HOME 指向 JDK 17+
# sliver: https://github.com/BishopFox/sliver/releases 下载对应平台
```

---

## 四、安装后验证

```bash
# 1. Windows 侧
python main.py tools

# 2. WSL 侧
wsl -d Ubuntu -e bash -lc 'which nmap sqlmap nuclei && nmap --version | head -1'

# 3. httpx 真身确认（必须是 projectdiscovery 版，不是 Python 库）
httpx -version    # 输出含 projectdiscovery 才对
```

预期：`python main.py tools` 的可用数从 **0/10** 上升到接近 **10/10**。

---

## 五、真身陷阱（务必注意）

| 工具名 | 陷阱 | 识别方法 |
|---|---|---|
| httpx | Python 库 CLI 与 PD 扫描器同名 | `httpx -version` 须含 `projectdiscovery` |
| ncat / nc | Windows/WSL 均有但功能不同 | 用 `nc -h` 看是否 ncat |
| python | Windows Store 别名可能劫持 | 用绝对路径 |

本 skill 的 `tools/base.py` 已内置真身校验（`verify_substr`），同名假货会被自动挡下。

---

## 六、分档安装建议

| 档位 | 装什么 | 适合 |
|---|---|---|
| 最小可用 | 通道 A（PD 全家桶 + ffuf + gobuster） | 先跑通 Web 打点流程 |
| Web 完整 | 最小 + 通道 B 的 sqlmap/dirsearch/wfuzz | Web 渗透主力 |
| 内网完整 | Web 完整 + 通道 D 全部 + impacket/netexec/certipy | 域渗透 |
| 全量 | 所有通道 | 一条龙全能力 |
