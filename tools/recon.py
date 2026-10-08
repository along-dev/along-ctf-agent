"""信息收集模块：封装 subfinder / httpx。

只负责"编排现成工具"，不自己实现子域爆破或存活探测的算法。
每个函数返回结构化结果，同时由 RunContext 落盘原始输出。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .base import RunContext, RunResult, run_tool


@dataclass
class ReconResult:
    subdomains: list[str] = field(default_factory=list)
    live_hosts: list[dict] = field(default_factory=list)
    raw: list[RunResult] = field(default_factory=list)


def enum_subdomains(domain: str, ctx: RunContext | None = None) -> RunResult:
    """子域枚举。subfinder 每行输出一个域名。"""
    out_file = ctx.path_for(f"subfinder_{domain}", "txt") if ctx else None
    args = ["-d", domain, "-all", "-silent"]
    if out_file:
        args += ["-o", str(out_file)]
    return run_tool("subfinder", args, ctx=ctx)


def probe_live(targets: Path | list[str], ctx: RunContext | None = None) -> RunResult:
    """存活探测 + 指纹。httpx -json 每行一个 JSON 对象。"""
    if isinstance(targets, Path):
        args = ["-l", str(targets), "-json", "-silent", "-sc", "-title", "-tech-detect"]
    else:
        args = ["-json", "-silent", "-sc", "-title", "-tech-detect"]
    return run_tool("httpx", args, ctx=ctx)


def run_recon(domain: str, ctx: RunContext | None = None) -> ReconResult:
    """被动 + 主动一条龙：子域 → 存活。产出资产清单。"""
    ctx = ctx or RunContext.create()
    result = ReconResult()

    sub = enum_subdomains(domain, ctx)
    result.raw.append(sub)

    subs: list[str] = []
    if sub.ok and sub.stdout:
        subs = [line.strip() for line in sub.stdout.splitlines() if line.strip()]
    if not subs:
        subs = [domain]  # 兜底：至少探测主域
    result.subdomains = subs

    subs_file = ctx.path_for("subdomains", "txt")
    subs_file.write_text("\n".join(subs), encoding="utf-8")

    live = probe_live(subs_file, ctx)
    result.raw.append(live)
    if live.ok and live.stdout:
        for line in live.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                result.live_hosts.append(json.loads(line))
            except json.JSONDecodeError:
                result.live_hosts.append({"url": line})

    # 汇总落盘
    summary = ctx.path_for("recon_summary", "json")
    summary.write_text(
        json.dumps(
            {"domain": domain, "subdomains": subs, "live_hosts": result.live_hosts},
            ensure_ascii=False, indent=2,
        ),
        encoding="utf-8",
    )
    return result
