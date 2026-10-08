# TOOLS.md — 工具调用层与工具目录

本 skill 的工具分两层：**编排层**（Python，写在 `tools/`）和**执行层**（外部 CLI 工具）。编排层只负责调度，执行层才是真干活的手脚。

## 一、编排层接口（Python）

位置：项目根 `tools/`。AI 负责决策，这些函数负责把决策变成工具调用。

### 核心入口：`run_tool(name, args)`

```python
from tools import RunContext, run_tool

ctx = RunContext.create("runs")                       # 建一次运行，输出自动落盘
r = run_tool("nmap", ["-sV", "-T4", "-p", "-", "TARGET"], ctx=ctx)

r.ok            # 是否成功
r.stdout        # 工具标准输出
r.output_files  # 落盘的文件路径
r.error         # 出错原因（工具没装等）
```

关键参数：
- `ctx` — 给输出上下文，stdout/stderr 自动存到 `runs/<run_id>/`，可追溯。
- `dry_run=True` — 只构建命令不执行。**没装工具也能验证编排逻辑**，适合先对命令再实跑。
- `timeout` — 覆盖默认超时。

### 环境探测：`probe_tools()` / `print_probe()`

编排前先知道哪些工具真装了。带**真身校验**——比如 Python 的 `httpx` 库和 ProjectDiscovery 的 `httpx` 扫描器同名，靠 `verify_substr` 把假货认出来，不会误判。

```bash
python main.py tools      # 打印工具可用性表
```

### 模块封装

| 模块 | 函数 | 作用 |
|---|---|---|
| `tools/recon.py` | `run_recon(domain)` | 子域 → 存活，一条龙出资产清单 |
| `tools/scanner.py` | `scan_ports` / `scan_vulns` / `test_sqli` / `fuzz_dirs` | 端口 / nuclei / SQLi / 目录 |
| `tools/report.py` | `render_report` / `write_report` | 汇总产出 MD 报告 |

### 设计约束
- **不拼 shell 字符串**：argv 用 list 传参，杜绝命令注入。
- **不自造轮子**：底层扫描能力一律编排现成工具。
- **换工具只改 `tools/base.py` 的注册表**，上层不动。

## 二、执行层工具目录（CLI）

> ⚠️ **本机实测（2026-10-08）**：以下工具**大多未安装**，Windows 与 WSL 两侧均缺。
> 完整缺失清单、安装命令、验证方法见 **`TOOLS-STATUS.md`**。
> 安装状态用 `python main.py tools` 实时探测（同一二进制名可能被其他程序占用，以探测为准）。
> 装好前，编排逻辑可用 `dry_run=True` 验证。

### 侦察 / 测绘（P0，先装这批）

| 工具 | 用途 | 常用参数 |
|---|---|---|
| subfinder | 子域枚举 | `-d <domain> -all -silent` |
| httpx | 存活 / 指纹 | `-l <list> -json -sc -title -tech-detect` |
| nmap | 端口 / 服务 | `-sV -sC -T4 -p- -oA <out>` |
| masscan | 高速全网段 | `-p1-65535 --rate=1000` |
| ffuf | 目录 / 参数 fuzz | `-u <url>/FUZZ -w <wl> -fc 404` |
| dirsearch | 目录爆破 | `-u <url> -e php,asp,jsp` |

### 漏洞验证

| 工具 | 用途 | 常用参数 |
|---|---|---|
| nuclei | 模板扫描 | `-severity critical,high -t cves/` |
| sqlmap | SQL 注入 | `-u <url> --batch --level=5 --risk=3` |

手动验证面：XSS、SSRF、SSTI、LFI、命令注入、反序列化、JWT、逻辑缺陷。手法见 `PLAYBOOK.md`。

### 内网 / 后渗透

| 工具 | 用途 |
|---|---|
| impacket | psexec / wmiexec / secretsdump / GetUserSPNs |
| msfconsole | 综合利用框架 |
| sliver | C2，上线与后渗透 |
| hashcat | 哈希破解（`-m 1000` NTLM / `-m 1800` sha512crypt） |

### 逆向 / CTF

| 工具 | 用途 |
|---|---|
| ghidra | 反编译 / 静态分析 |
| frida | 动态插桩、脱壳、hook |

## 三、扩展新工具（三步）

1. 在 `tools/base.py` 的注册表加一行 `register(ToolSpec(...))`。
2. 若有同名假货，补 `verify_flag` + `verify_substr`。
3. 想封装成模块函数，就在 `recon/scanner/report` 里加一个调用它的函数。

```python
register(ToolSpec(
    "nikto", "nikto", "scan", "Web 服务器扫描",
    verify_flag="-Version", verify_substr="nikto", timeout=900,
))
```
