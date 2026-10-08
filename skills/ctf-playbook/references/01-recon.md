# 01 信息收集（外网打点 & 资产探测）

**目标**：画出门——资产、子域、端口、前端 API、目录，形成资产表喂给 02 扫描。

## 检查清单（按序执行）

1. **确认范围**：记录 `TARGET_ORG`、授权域名 `HOST`、授权 IP/CIDR、禁止触碰项、输出目录。
2. **建资产表**：先建表再收集，字段 `asset,type,ip,port,protocol,title,source,status,evidence`。状态用 candidate/observed/negated/interesting。
3. **资产测绘**：用 FOFA / HUNTER(奇安信) / Goby / Shodan 查组织名、域名、证书、标题关键词；导出候选资产后**去重**（同域名同端口只留一条）。
4. **子域名收集**：被动(证书透明度/搜索引擎/备案) + 工具聚合(OneForAll、dddd)，再 DNS 解析验证 + HTTP 验证。优先看 `dev/test/admin/old/stage/beta/api/sso` 命名。
5. **企业/公开信息**：ENScan_GO(ICP备案/APP/小程序/公众号)、AppInfoScanner(移动端/前端域名与接口)。关注招聘 JD 透露技术栈、GitHub 泄露的密钥/配置。
6. **前端/API 探测**：DevTools Network 抓 XHR；下载 JS 搜 `api|swagger|graphql|admin|v1|token|upload|callback`；有 APP 样本就 AppInfoScanner 提取。
7. **目录/后台扫描**：dirsearch（或等价），`-e php,html,js,txt`，先小字典低线程，先建 404 baseline。
8. **整理证据**：资产总表 `assets.csv` + 高价值入口 `interesting-assets.md` + 证据目录 `raw/ img/`。

## 工具（可核验来源）

- 测绘：FOFA、HUNTER、Goby、Shodan、Censys、ZoomEye、Quake
- 子域：OneForAll、dddd
- 企业/APP：ENScan_GO、AppInfoScanner
- 目录：dirsearch、Golin、goon、FuzzScanner
- 本地搜索：Everything（Windows 文件定位）
- 待核验名（不硬编功能）：apitool、vuescan、webpackscan、dirscan_3.0、ydirscan、webfinder-next、fine、jx11

## 关键命令速查（占位目标）

```bash
# DNS 解析验证
nslookup HOST; dig HOST ANY
# HTTP 基线
curl -sSI https://HOST/ -o raw/root-headers.txt
curl -s https://HOST/ -o raw/root-body.html
# 证书 SAN（暴露子域）
openssl s_client -connect HOST:443 -servername HOST 2>/dev/null | openssl x509 -noout -text | grep -A1 "Subject Alternative Name"
# 子域收集
python3 oneforall.py --target HOST run
# 前端 JS 关键词（下载后本地搜）
grep -RniE "api|swagger|graphql|admin|v1|token|upload|callback" ./frontend_source/
# 目录扫描（先建 404 baseline）
dirsearch -u https://HOST -e php,html,js,txt -o raw/dirsearch.txt
# 源码泄露定向探测（非大字典）
for p in .git/HEAD .git/config .env www.zip backup.zip index.php.bak robots.txt; do
  echo -n "$p "; curl -s -o /dev/null -w "%{http_code}\n" https://HOST/$p; done
```

## 关键判断

- 能解析 ≠ 能访问；能访问 ≠ 属于目标；404 ≠ 没价值（可能暴露框架/网关/错误页特征）。
- 目录扫描别只看状态码：看**响应长度 + 标题**；`403` 记线索不当下结论；`404` 长度一致是统一 404 页，建 baseline。
- 高价值关键词：`admin api test dev stage beta old backup sso auth login swagger graphql upload file manage console internal`。

## 证据模板

| 域名 | IP | 端口 | 协议 | 标题/指纹 | 来源 | 证据 |
|---|---|---:|---|---|---|---|---|
| api.HOST | TARGET | 443 | HTTPS | API Gateway | FOFA | raw/api-curl.txt |

一个发现要站得住，需 5 样：来源、证据、可复现方式、风险解释、范围确认。

## 防守视角
你做的每步查询都在测绘平台的日志里留下检索痕迹；目录扫描在 Web access log 里是密集 404/403。

## 常见误区
资产越多越好（错，未验证=噪声）｜只用一个工具｜看到 403 当漏洞｜看标题认定框架｜不存原始证据｜大字典高线程硬扫。
