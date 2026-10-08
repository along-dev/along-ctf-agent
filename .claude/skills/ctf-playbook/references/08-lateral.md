# 08 内网横向 & 后渗透 & 权限维持

**目标**：拿到一台机器后，向更多机器/账号延伸并长期驻留；同时会防守检测。

## 典型链条
```
入口机器 → 凭证收集 → 账号复用 → 远程服务登录 → 横向移动 → 权限扩大 → 持久化 → 数据访问/外传
```

## 检查清单

1. **凭证抓取**：Mimikatz（研究用途）从 LSASS/系统/缓存取凭证。防守：Credential Guard、管理员分层、LAPS、监控 LSASS 异常访问。
2. **C2 远控**：Cobalt Strike 是合法红队工具（也常被滥用）。检测 beacon 周期外连、JA3/JA4/TLS 指纹、进程注入、异常父子进程。
3. **横向移动**：SMB/Admin Share、WMI、WinRM、RDP、SSH、数据库跳板。记录 `source_host/source_user/target_host/protocol/credential_source/evidence/impact/cleanup`。
4. **持久化**：计划任务(T1053)、注册表 Run Key(T1547.001)、Windows 服务(T1543.003)、WMI 订阅(T1546.003)、SSH authorized_keys、WebShell 文件。检查新增服务/任务/启动项/账号/SSH key/Web 目录。
5. **画时间线**：initial-access → credential-access → lateral-movement → persistence → cleanup，Mermaid 时序图。

## 工具（可核验来源）
Mimikatz、Cobalt Strike、Ladon。待核验：goexec、gorailgun、alien、yongheng、hearts（不硬编功能）。

## 证据模板（横向移动记录）
```text
source_host / source_user / target_host / protocol
credential_source / evidence(日志路径·时间·事件ID·截图)
impact / cleanup
```

## 防守视角
登录事件 4624（登录类型）、WMI 事件、WinRM/PowerShell 日志、新增服务/计划任务/注册表、SSH auth.log、C2 周期 beacon——横向和持久化的每一步都有对应日志。检测看行为，不看工具名。

## 常见误区
拿一台机器=拿下内网（需凭证+网络+权限）｜只查漏洞不查凭证（后渗透靠凭证复用）｜只删 WebShell（可能还有账号/服务/任务）｜只看工具名｜不做时间线。
