# 07 本地提权（低权限 → 高权限）

**目标**：已进房间但权限低，尝试升权。**先查配置，再查 CVE**（配置提权比 CVE 更常见）。

## 两类提权
- **漏洞提权**：内核/服务已知漏洞（绑定 CVE + 版本 + 补丁状态）
- **配置提权**：权限/服务/计划任务/sudo/ACL/凭证泄露的错误配置

## 检查清单

1. **记录当前权限**（提权前后都要记，否则无法证明"提升"）。
2. **Windows 查**：服务路径未加引号、服务可写、计划任务可写、启动目录可写、AlwaysInstallElevated、凭证文件、SeImpersonatePrivilege、UAC、补丁缺失。
3. **Linux 查**：`sudo -l` 规则、SUID/SGID 文件、cron 可写脚本、PATH 劫持、Docker 组权限、内核版本、明文凭证(history/env/配置)。
4. **CVE 必须绑定版本**：CVE-2021-3156(sudo Baron Samedit)、CVE-2016-5195(Dirty COW)、CVE-2021-34527(PrintNightmare)——写清本机版本+补丁状态，靶场复现≠生产可利用。
5. **heapdump/进程内存**：Spring Boot Actuator heapdump 可能含 Token/连接串/用户数据；取证先确认端点是否暴露，别直接下载大文件，敏感值脱敏。

## 工具状态
图中 `tiquan`、`yanni`、`PotatoTool.jar` 均**无稳定官方来源，标待核验**。`heapdump` 是真实概念（Spring Boot Actuator）。通用思路：linpeas / winpeas（枚举）、GTFOBins（SUID/sudo 利用参考）。

## 关键命令速查（占位目标，只读枚举优先）

```bash
# 提权前基线
id; whoami; hostname; uname -a; cat /etc/os-release
# sudo 规则 + 版本
sudo -l; sudo -V
# SUID/SGID + capabilities
find / -perm -4000 -type f 2>/dev/null
getcap -r / 2>/dev/null
# cron 可写脚本
cat /etc/crontab; ls -la /etc/cron.d /etc/cron.daily 2>/dev/null
# 可写目录（PATH 劫持线索）
find / -writable -type d 2>/dev/null | grep -v '^/proc' | head -50
# 明文凭证（脱敏）
grep -rEi 'pass(wd|word)?|token|secret|key' ~/. /etc /opt /var 2>/dev/null | head
# Docker 组
id | grep -E 'docker|lxd'
# 常用 CVE 版本范围（必须核对发行版 backport）
#   CVE-2016-5195 Dirty COW（内核 <4.8.3）
#   CVE-2022-0847 Dirty Pipe（5.8 ~ 5.16.11）
#   CVE-2021-3156 sudo Baron Samedit（sudo 1.8.2~1.8.31）
#   CVE-2021-4034 PwnKit（老版 polkit/pkexec）
# 参考字典：GTFOBins(sudo/SUID)、linpeas/winpeas(枚举)
```

## 证据模板（cve-candidates.md）
```markdown
## CVE-XXXX-YYYY
- 组件 COMPONENT；当前版本 VERSION；影响版本(摘自 NVD/厂商)
- 补丁状态 installed/missing/unknown
- 本地证据 COMMAND_OUTPUT_PATH
- 风险 local privilege escalation / information disclosure
- 结论 observed / negated / needs-lab-proof
```

## 提权证明分级（同 03）
hypothesis → observed → primitive → local_proof → remote_proof。禁止："内核版本老"写成"能 root"、"sudo 规则异常"写成"已拿 root"。

## 防守视角
服务/计划任务/注册表变更、sudo 日志、异常 dump、异常服务创建、敏感进程访问，都在审计日志里。

## 常见误区
看到老版本就说可提权（补丁可能 backport）｜只找 CVE 忽略配置｜生产直接跑 EXP（先本地同版本复现）｜heapdump 直接下载分析｜不记录当前权限。
