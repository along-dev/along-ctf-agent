# 10 空间测绘打点 & 弱口令后台（测绘语法 → 命中 → 登录）

**目标**：用测绘平台（Shodan/FOFA/Quake/Hunter）的**检索语法**先圈出暴露面，命中一批「疑似后台/面板」，再最小影响地验证可达性，最后低风险衔接弱口令。定位是 01 的**低成本替代/补充**：不是扫，是搜——先把答案搜出来，再去验证。

> 铁律提醒：测绘命中只代表「平台索引里存在特征」，**不等于目标可控、更不等于属于你的授权范围**。命中 → 可达 → 归属 → 授权，四步验证完才允许深入。

## 检查清单（按序执行）

1. **确认授权边界**：测绘检索会翻到大量**非授权**目标。先明确「允许触碰的资产特征」（自有域名、指定 CIDR、客户资产清单），命中结果必须先用**归属证据**（证书 SAN、WHOIS、ICP 备案、页面版权/联系信息）过滤，非授权目标**只记录不交互**。
2. **选对平台与语法**：Shodan（全球、`http.title`/`http.html`）、FOFA（`title`/`body`/`header`/`cert`，中文资产多）、Quake（`service`/`app`）、Hunter（奇安信，ICP 关联强）。同一检索词多平台交叉，命中率更高。
3. **测绘检索**：先用**标题 + 正文组合语法**定位面板（见下方语法速查），再用 `port`/`country`/`org` 收窄；非标端口（8080/8888/8443）往往防护更弱、后台暴露概率更高。
4. **整理命中表**：把结果落到资产表（复用 01 的字段），**去重**（同 IP 同端口只留一条），标注检索来源与命中时间，导出候选清单。
5. **可达性与指纹验证**：对**授权内**候选逐个 `curl -sSI` 取状态码/标题/`Server`/`Set-Cookie`，确认是不是真后台（登录框 / 管理界面 / 面板特征），而不是停机页、蜜罐、仿冒页。**只做无害 GET，不发登录请求。**
6. **后台类型识别**：JS 框架特征（Vue/React 打包 hash）、接口路径（`/api/login`、`/admin`）、认证形态（表单/Token/Basic/OAuth）。这决定后面走弱口令（06）还是别的入口。
7. **弱口令衔接**（转 06，先写计划）：确认是登录后台后，**先手工**试少量高概率默认口令（`admin/admin`、`admin/123456`、`root/root` 等），命中即停；手工不中再按 06 的**速率/停止条件**上轻度字典。**禁止无边界爆破。**
8. **收尾取证**：命中与验证过程全部留证，写入 `artifacts/10-mapping/`。

## 测绘语法速查（占位，检索用）

```text
# —— Shodan ——
http.title:"bot" port:443
http.title:"telegram" http.html:"bot"
http.title:"panel" http.html:"telegram"
http.html:"bot_token"
http.title:"dashboard" http.html:"/bot"

# —— FOFA ——
title="Bot" && body="telegram"
body="bot_token" && port="443"
title="Dashboard" && body="bot" && country="CN"
header="nginx" && body="telegram_bot"
# 非标端口常防护更弱：
body="bot" && port="8080"

# —— 通用后台/面板检索词（按需替换 title/body）——
title="管理" || title="后台" || title="登录" && body="admin"
header="Set-Cookie" && body="JWT" && title="console"
cert="HOST"                 # 用证书反查同证书资产
```

**语法差异提醒**：不同平台支持的字段/操作符不同（如 FOFA 用 `=` 与 `&&`，Shodan 用 `:` 与空格隐式 AND），字段名也不统一（Shodan `http.html` ↔ FOFA `body`）。以各平台官方文档为准，命中字段写进证据。

## 工具（可核验来源）

- 测绘：Shodan、FOFA、Quake、Hunter(奇安信)、Censys、ZoomEye
- 可达性/指纹：curl、whatweb、浏览器 DevTools
- 弱口令衔接：见 06（hydra / medusa / Burp Intruder），**先写计划再跑**

## 关键命令速查（占位目标，无害 GET 优先）

```bash
# 可达性与指纹（只取响应头/标题，不发登录）
curl -sSI https://HOST/ -o raw/HOST-headers.txt
curl -s  https://HOST/ -o raw/HOST-body.html
grep -io "<title>[^<]*</title>" raw/HOST-body.html

# 归属证据（确认是否在授权范围内）
echo | openssl s_client -connect HOST:443 -servername HOST 2>/dev/null | openssl x509 -noout -text | grep -A1 "Subject Alternative Name"

# 弱口令衔接仅作示例：务必先按 06 写速率与停止条件，命中即停
# hydra -L users.txt -P pass.txt -f -t 1 -W 2 https-post-form \
#   "/login:user=^USER^&pass=^PASS^:F=incorrect"
```

## 关键判断

- **命中 ≠ 脆弱**：平台显示「标题含 bot」不代表你能登录，更不代表有漏洞，只是「值得看一眼」。
- **归属先于交互**：测绘结果里混着大量别人的资产。没有归属证据前，**不做任何带认证/写入/爆破的动作**。
- **非标端口是线索不是结论**：8080/8888 上跑后台 ≠ 一定弱口令，只是「统计上更值得先看」。
- **手工优先**：默认口令命中率不低，成本极低，上线前先手工，别一上来就堆字典。

## 证据模板（mapping-hits.csv / notes）

```markdown
## 检索
- 平台 shodan.io / fofa.info；语法 'http.title:"telegram" http.html:"bot"'；时间 STAMP
## 命中（原始）
- 导出 raw/fofa-page1.json；命中 N 条
## 归属过滤
- IP TARGET；证书 SAN 命中授权域名 HOST；ICP 备案 ORG      → in-scope
- IP x.x.x.x；无归属证据                                     → out-of-scope（只记录，未交互）
## 可达性验证
- GET https://HOST/ → 200；title="Bot 管理后台"；Server="nginx"；证据 raw/HOST-headers.txt
## 结论
- 级别 observed（存在后台登录页）；是否可登录 = 未测试 / 待 06
```

## 防守视角

你的每一次测绘检索都留在**平台侧日志**（账号 + 关键词 + 时间），部分平台会向资产方告警「有人查了你的资产」。命中后对目标的 GET/登录尝试会落到目标 Web access log：来自测绘平台爬虫之外的**新来源 IP**、对 `/login` 的试探性请求、同一来源短时多账号尝试，都是可观测信号。**你查了什么，本身就是可追溯的。**

## 常见误区

命中就当成漏洞｜对非授权命中直接交互/爆破｜只用一个平台｜忽略非标端口｜看到登录页就无边界爆破｜不做归属校验（把别人的资产当成目标）｜把平台索引时间当资产现状。
