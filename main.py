"""红队 Agent 入口编排。

AI 是"大脑"，这个文件是"脑干"——把各模块串成可执行的命令行流程。
子命令：
  tools            探测本机工具链可用性
  recon <domain>   信息收集（子域 + 存活）
  scan  <target>   端口 + 漏洞扫描
  report           汇总最近一次运行生成报告

用法：
  python main.py tools
  python main.py recon example.com
  python main.py scan 1.2.3.4 --ports - --nuclei
"""

from __future__ import annotations

import argparse
import sys

from tools import RunContext, print_probe, recon, scanner, report

# Windows 控制台默认 GBK，强制 UTF-8 避免中文乱码
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass


def _cmd_tools(args: argparse.Namespace) -> int:
    print_probe()
    return 0


def _cmd_recon(args: argparse.Namespace) -> int:
    ctx = RunContext.create(args.out)
    print(f"[*] 运行目录：{ctx.root}")
    result = recon.run_recon(args.domain, ctx)
    print(f"[+] 子域：{len(result.subdomains)}  存活：{len(result.live_hosts)}")
    for h in result.live_hosts[:20]:
        print(f"    {h.get('url', h)}")
    print(f"[+] 汇总：{ctx.path_for('recon_summary', 'json')}")
    return 0


def _cmd_scan(args: argparse.Namespace) -> int:
    ctx = RunContext.create(args.out)
    print(f"[*] 运行目录：{ctx.root}")
    nuclei_targets = args.target if args.nuclei else None
    result = scanner.run_scan(args.target, nuclei_targets=nuclei_targets,
                              ctx=ctx, ports=args.ports)
    print(f"[+] 完成，原始输出见：{ctx.root}")
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    findings = []
    for item in args.finding or []:
        # 格式：name,severity,asset
        parts = [p.strip() for p in item.split(",")]
        if len(parts) >= 3:
            findings.append(report.Finding(name=parts[0], severity=parts[1], asset=parts[2]))
    content = report.render_report(target=args.target, findings=findings,
                                   scope=args.scope)
    out = report.write_report(content, args.output)
    print(f"[+] 报告已生成：{out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="redteam-agent",
                                description="红队编排入口（授权测试用）")
    p.add_argument("--out", default="session-data/temp/runs", help="输出根目录（默认 session-data/temp/runs/）")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("tools", help="探测工具链可用性")
    sp.set_defaults(func=_cmd_tools)

    sp = sub.add_parser("recon", help="信息收集")
    sp.add_argument("domain")
    sp.set_defaults(func=_cmd_recon)

    sp = sub.add_parser("scan", help="端口 + 漏洞扫描")
    sp.add_argument("target")
    sp.add_argument("--ports", default="-", help="端口范围，默认 -（全端口）")
    sp.add_argument("--nuclei", action="store_true", help="附加 nuclei 扫描")
    sp.set_defaults(func=_cmd_scan)

    sp = sub.add_parser("report", help="生成报告")
    sp.add_argument("target")
    sp.add_argument("--scope", default="")
    sp.add_argument("--output", default="report.md")
    sp.add_argument("--finding", action="append",
                    help="漏洞项，格式 name,severity,asset（可多次）")
    sp.set_defaults(func=_cmd_report)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
