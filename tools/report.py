"""报告生成模块：把各阶段产出汇总成 MD 报告。

只负责把结构化结果渲染成报告文本，不做任何扫描/验证动作。
PDF 转换交给外部工具（pandoc / wkhtmltopdf），这里只出 MD。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class Finding:
    name: str
    severity: str            # critical / high / medium / low / info
    asset: str
    description: str = ""
    repro: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    fix: str = ""


SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
SEVERITY_CN = {"critical": "严重", "high": "高危", "medium": "中危",
               "low": "低危", "info": "信息"}


def _counts(findings: list[Finding]) -> dict[str, int]:
    counts = {k: 0 for k in SEVERITY_ORDER}
    for f in findings:
        counts[f.severity.lower()] = counts.get(f.severity.lower(), 0) + 1
    return counts


def render_report(*, target: str, findings: list[Finding],
                  recon: dict | None = None, scan: dict | None = None,
                  scope: str = "[范围]", author: str = "子龙") -> str:
    date = datetime.now().strftime("%Y-%m-%d")
    counts = _counts(findings)
    ranked = sorted(findings, key=lambda f: SEVERITY_ORDER.get(f.severity.lower(), 9))

    lines: list[str] = []
    lines.append(f"# 渗透测试报告 · {target}\n")
    lines.append(f"- 目标范围：{scope or target}")
    lines.append(f"- 测试时间：{date}")
    lines.append(f"- 测试方：{author}\n")

    # 执行摘要
    lines.append("## 1. 执行摘要\n")
    lines.append("| 严重级别 | 数量 |")
    lines.append("|---|---|")
    for sev, n in counts.items():
        lines.append(f"| {SEVERITY_CN[sev]} {sev} | {n} |")
    total = sum(counts.values())
    lines.append(f"\n共发现 **{total}** 个问题，其中高危及以上 "
                 f"{counts['critical'] + counts['high']} 个。\n")

    # 资产清单
    if recon:
        lines.append("## 2. 资产清单\n")
        subs = recon.get("subdomains", [])
        hosts = recon.get("live_hosts", [])
        lines.append(f"- 子域数量：{len(subs)}")
        lines.append(f"- 存活主机：{len(hosts)}\n")
        if hosts:
            lines.append("| URL | 状态码 | 标题 | 指纹 |")
            lines.append("|---|---|---|---|")
            for h in hosts[:100]:
                lines.append(
                    f"| {h.get('url', '-')} | {h.get('status_code', '-')} "
                    f"| {h.get('title', '-')} | {','.join(h.get('tech', []) or [])} |"
                )
            lines.append("")

    # 漏洞详情
    lines.append("## 3. 漏洞详情\n")
    if not ranked:
        lines.append("_本次未发现已验证漏洞。_\n")
    for i, f in enumerate(ranked, 1):
        lines.append(f"### 3.{i} {f.name}\n")
        lines.append(f"- **风险等级**：{SEVERITY_CN.get(f.severity.lower(), f.severity)}")
        lines.append(f"- **影响资产**：{f.asset}")
        if f.description:
            lines.append(f"- **描述**：{f.description}")
        if f.repro:
            lines.append("- **复现步骤**：")
            for j, step in enumerate(f.repro, 1):
                lines.append(f"  {j}. {step}")
        if f.evidence:
            lines.append("- **证据**：")
            for ev in f.evidence:
                lines.append(f"  - `{ev}`")
        if f.fix:
            lines.append(f"- **修复建议**：{f.fix}")
        lines.append("")

    lines.append("## 4. 附录\n")
    lines.append("- 工具链：nmap / nuclei / sqlmap / subfinder / httpx / ffuf")
    lines.append(f"- 报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return "\n".join(lines)


def write_report(content: str, out_path: str | Path) -> Path:
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p
