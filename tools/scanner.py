"""扫描与漏洞验证模块：封装 nmap / nuclei / sqlmap / ffuf。

原则：AI 负责编排决策（扫哪些端口、用哪些模板、验证哪个参数），
底层扫描能力一律交给现成工具，不自己造轮子。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .base import RunContext, RunResult, run_tool


@dataclass
class ScanResult:
    target: str
    open_ports: list[dict] = field(default_factory=list)
    findings: list[dict] = field(default_factory=list)
    raw: list[RunResult] = field(default_factory=list)


def scan_ports(target: str, ports: str = "-", rate: int | None = None,
               ctx: RunContext | None = None) -> RunResult:
    """端口 / 服务扫描。-p- 全端口，-p 指定。"""
    args = ["-sV", "-sC", "-T4", "-p", ports, target, "-oX",
            str(ctx.path_for(f"nmap_{target}", "xml")) if ctx else "-"]
    if rate:
        args = ["--min-rate", str(rate), *args]
    return run_tool("nmap", args, ctx=ctx)


def scan_vulns(targets, severity: str = "critical,high",
               templates: str = "cves/", ctx: RunContext | None = None) -> RunResult:
    """nuclei 模板扫描。severity 过滤严重级别。"""
    from pathlib import Path
    args = ["-severity", severity, "-t", templates, "-silent"]
    if isinstance(targets, (str, Path)) and str(targets).endswith((".txt",)):
        args = ["-l", str(targets), *args]
    else:
        args = ["-u", str(targets), *args]
    return run_tool("nuclei", args, ctx=ctx)


def test_sqli(url: str, level: int = 3, risk: int = 2, request_file: str | None = None,
              ctx: RunContext | None = None) -> RunResult:
    """SQL 注入最小化验证。有抓包文件优先用 -r。"""
    if request_file:
        args = ["-r", request_file, "--batch", f"--level={level}", f"--risk={risk}"]
    else:
        args = ["-u", url, "--batch", f"--level={level}", f"--risk={risk}"]
    return run_tool("sqlmap", args, ctx=ctx)


def fuzz_dirs(base_url: str, wordlist: str, code_filter: str = "404",
              ctx: RunContext | None = None) -> RunResult:
    """目录 / 文件 fuzz。base_url 里用 FUZZ 占位。"""
    args = ["-u", base_url, "-w", wordlist, "-fc", code_filter, "-silent"]
    return run_tool("ffuf", args, ctx=ctx)


def run_scan(target: str, *, nuclei_targets=None, ctx: RunContext | None = None,
             ports: str = "-") -> ScanResult:
    """编排：端口扫描 → 漏洞扫描。产出攻击面 + 初步发现。"""
    ctx = ctx or RunContext.create()
    result = ScanResult(target=target)

    port_res = scan_ports(target, ports=ports, ctx=ctx)
    result.raw.append(port_res)

    if nuclei_targets:
        vuln_res = scan_vulns(nuclei_targets, ctx=ctx)
        result.raw.append(vuln_res)

    return result
