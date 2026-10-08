# 02 漏洞扫描 & 资产探测

**目标**：搞清门后是什么锁、锁是不是旧型号、有没有公开已知问题。扫描给线索，不是结论。

## 流程（牢记：扫描 ≠ 漏洞成立）

```
资产确认 → 指纹识别 → 版本/配置判断 → 漏洞假设 → 低风险验证 → 人工复核 → 证据归档
```

## 检查清单

1. **输入资产表**：只放已授权、已验证存活的 HOST/IP。
2. **先跑低风险模式**：端口、标题、指纹、版本，不跑破坏性 POC。
3. **分类扫描**：
   - 综合：xray、afrog、kscan、fscan、TscanPlus（输出原始 JSON 存 raw/）
   - Java 反序列化：确认 Fastjson/Jackson/Shiro/Struts2/Log4j 版本与危险配置（AutoType、rememberMe 固定密钥、上传解析链路、JNDI lookup）
   - CMS：ThinkPHP、若依/RuoYi（看路由/报错/静态路径特征，回版本）
   - 中间件：JBoss、Jenkins、WebLogic、XXL-JOB、Docker（看版本/默认 token/未授权 API）
   - 设备/虚拟化：vCenter、Hikvision、OA（看型号/固件版本/暴露接口）
4. **对命中的 CVE 人工复核**：对照 NVD/厂商公告/CISA KEV 的条件逐条核（版本、组件、配置、补丁状态、请求路径）。
5. **高危先查 CISA KEV** 排序。
6. **写 manual-review.md**：逐条写「为什么认为存在/为什么否定」。

## 关键命令速查（占位目标）

```bash
# 指纹（响应头 + 页面特征）
curl -sSI https://HOST/
# 常见框架特征快速判别
#   Shiro   → Set-Cookie: rememberMe=deleteMe
#   Struts2 → 以 .action/.do 结尾的 URL
#   ThinkPHP→ 报错暴露 /thinkphp 路由或框架路径
#   Spring Boot Actuator → /actuator/env /actuator/heapdump
# 定向中间件探测（低风险，单次）
for p in /actuator /console /manager/html /jenkins /api /swagger-ui.html; do
  echo -n "$p "; curl -s -o /dev/null -w "%{http_code}\n" https://HOST$p; done
# 若需自动化扫描器（先指纹再 POC，低速率）
#   xray webscan / afrog -t HOST / nuclei -u HOST -rl 5
```

## 关键判断

- 扫描器报高危 ≠ 漏洞成立（模板可能误报、条件可能不满足）。
- CVSS 高 ≠ 当前资产可利用。结合暴露面、是否有补丁、业务重要性。
- 工具名待核验（不硬编）：Rscan、ppsscan、Xscan、supersql、PcapDecrypt、Seay-Svn、Gr33k、hvvoaexploit。

## 证据模板（manual-review.md）

```markdown
## CVE-XXXX-YYYY on https://HOST
- 来源：TOOL 输出 / 手工发现
- 组件：COMPONENT VERSION
- 厂商公告：LINK
- 影响条件：官方公告条件列表
- 本地证据：raw/xxx.txt、img/xxx.png
- 低风险验证：REQUEST_SUMMARY
- 结论：observed / negated / needs-auth / out-of-scope
```

## 报告用词规范
写「目标 /upload.action 响应头与错误页符合 Struts2，版本线索指向受影响范围，仍需确认补丁状态」，不写「已确认漏洞」。

## 防守视角
扫描器的高频请求、特征 UA、固定 payload 在 WAF/IDS 里是明显特征；靶场里往往也是失分点。

## 常见误区
扫描器报高危=漏洞｜一上来跑所有 POC｜只看 CVSS｜不记工具/模板版本｜只扫 Web 忽略中间件/设备。
