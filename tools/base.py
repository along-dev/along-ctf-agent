"""统一工具调用层。

核心思路：AI 是"大脑"，工具是"手脚"。所有外部工具都通过 run_tool(name, args)
一个入口调用，换工具只改这里，上层编排不用动。

- 不自造轮子：nmap/sqlmap/nuclei 这些直接编排现成的。
- 不拼 shell 字符串：argv 用 list 传参，杜绝命令注入。
- 每次调用落盘：原始输出存到 runs/<run_id>/，可追溯、可复现。
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Sequence


# --------------------------------------------------------------------------- #
# 工具注册表
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class ToolSpec:
    name: str                      # 逻辑名，run_tool 用这个
    binary: str                    # 实际可执行文件名（用 shutil.which 找）
    category: str                  # recon / scan / exploit / post / report ...
    description: str
    prefix: tuple[str, ...] = ()   # 每次调用前置的固定参数
    timeout: int = 600             # 默认超时（秒）
    verify_flag: str = ""          # 探测校验参数，如 "-version"
    verify_substr: str = ""        # 校验输出需包含的子串（识别同名假货）


TOOL_REGISTRY: dict[str, ToolSpec] = {}


def register(spec: ToolSpec) -> None:
    TOOL_REGISTRY[spec.name] = spec


# --- 侦察 / 测绘 ---
# verify_flag/verify_substr 用于识别"同名假货"：
# 比如 Python 的 httpx 库和 ProjectDiscovery 的 httpx 扫描器同名，
# 靠校验输出里的 "projectdiscovery" 关键字把真扫描器认出来。
register(ToolSpec("subfinder", "subfinder", "recon", "子域枚举",
                  verify_flag="-version", verify_substr="projectdiscovery"))
register(ToolSpec("httpx", "httpx", "recon", "存活探测 + 指纹识别",
                  verify_flag="-version", verify_substr="projectdiscovery"))
register(ToolSpec("nmap", "nmap", "scan", "端口 / 服务扫描",
                  verify_flag="--version", verify_substr="nmap"))
register(ToolSpec("masscan", "masscan", "scan", "全网段高速端口扫描",
                  verify_flag="--version", verify_substr="masscan"))
register(ToolSpec("ffuf", "ffuf", "scan", "目录 / 参数 / 子域 fuzz",
                  verify_flag="-V", verify_substr="ffuf"))
register(ToolSpec("dirsearch", "dirsearch", "scan", "目录爆破",
                  verify_flag="--version", verify_substr="dirsearch"))

# --- 漏洞验证 ---
register(ToolSpec("nuclei", "nuclei", "exploit", "模板化漏洞扫描",
                  verify_flag="-version", verify_substr="projectdiscovery"))
register(ToolSpec("sqlmap", "sqlmap", "exploit", "SQL 注入检测与利用",
                  verify_flag="--version", verify_substr="sqlmap"))

# --- 后渗透 / C2（按需扩展） ---
register(ToolSpec("sliver", "sliver-server", "post", "C2 服务端"))
register(ToolSpec("hashcat", "hashcat", "post", "哈希破解",
                  verify_flag="--version", verify_substr="hashcat"))


# --------------------------------------------------------------------------- #
# 运行上下文：管理输出目录与落盘
# --------------------------------------------------------------------------- #

@dataclass
class RunContext:
    root: Path                       # 输出根目录
    run_id: str
    calls: list[dict] = field(default_factory=list)

    @classmethod
    def create(cls, root: str | Path = "runs") -> "RunContext":
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = Path(root) / run_id
        base.mkdir(parents=True, exist_ok=True)
        return cls(root=base, run_id=run_id)

    def path_for(self, name: str, ext: str = "txt") -> Path:
        safe = name.replace("/", "_").replace("\\", "_")
        return self.root / f"{safe}.{ext}"


@dataclass
class RunResult:
    tool: str
    argv: list[str]
    returncode: int | None
    stdout: str
    stderr: str
    duration: float
    output_files: list[str] = field(default_factory=list)
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.returncode == 0

    def to_dict(self) -> dict:
        return {
            "tool": self.tool,
            "argv": self.argv,
            "returncode": self.returncode,
            "duration": round(self.duration, 2),
            "output_files": self.output_files,
            "error": self.error,
        }


# --------------------------------------------------------------------------- #
# 主入口
# --------------------------------------------------------------------------- #

def _resolve_binary(spec: ToolSpec) -> str | None:
    """找到可执行文件，并（若有校验规则）确认真身，避免同名假货。"""
    path = shutil.which(spec.binary)
    if path is None:
        return None
    if not spec.verify_flag:
        return path
    try:
        proc = subprocess.run(
            [path, spec.verify_flag], capture_output=True, text=True,
            timeout=15, encoding="utf-8", errors="replace",
        )
    except (OSError, subprocess.TimeoutExpired):
        return path  # 跑不起来就不否认真身，交给实际调用报错
    blob = f"{proc.stdout or ''}{proc.stderr or ''}".lower()
    if spec.verify_substr and spec.verify_substr.lower() not in blob:
        return None  # 名字对但真身不符（如同名的 python httpx 库）
    return path


def run_tool(
    name: str,
    args: Sequence[str] | None = None,
    *,
    ctx: RunContext | None = None,
    timeout: int | None = None,
    dry_run: bool = False,
    capture: bool = True,
) -> RunResult:
    """统一工具调用入口。

    name    : TOOL_REGISTRY 里的逻辑名
    args    : 传给工具的参数列表（不含 binary 本身）
    ctx     : 输出上下文，给了就把 stdout/stderr 落盘
    dry_run : 只打印将执行的命令，不真跑（无工具环境下也能验证编排）
    """
    args = list(args or [])

    spec = TOOL_REGISTRY.get(name)
    if spec is None:
        return RunResult(name, [], None, "", "", 0.0,
                         error=f"未注册的工具: {name}。可用: {sorted(TOOL_REGISTRY)}")

    # dry-run 先于 binary 检查：即使工具没装，也能验证编排出的命令是否正确
    binary = _resolve_binary(spec)
    if dry_run:
        exe = binary or spec.binary
        argv = [exe, *spec.prefix, *args]
        return RunResult(name, argv, 0, f"[dry-run] {' '.join(argv)}", "", 0.0)

    if binary is None:
        hint = (f"工具 '{spec.binary}' 不可用：未安装、不在 PATH，"
                f"或真身校验未通过（{spec.description}）。"
                f"用 dry_run=True 可先验证编排。")
        return RunResult(name, [], None, "", "", 0.0, error=hint)

    argv = [binary, *spec.prefix, *args]
    timeout = timeout or spec.timeout

    started = time.monotonic()
    try:
        proc = subprocess.run(
            argv,
            capture_output=capture,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired:
        return RunResult(name, argv, None, "", "", time.monotonic() - started,
                         error=f"超时（>{timeout}s）")
    except OSError as exc:
        return RunResult(name, argv, None, "", "", time.monotonic() - started,
                         error=f"执行失败: {exc}")

    duration = time.monotonic() - started
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""

    files: list[str] = []
    if ctx is not None:
        out_f = ctx.path_for(f"{name}", "out.txt")
        err_f = ctx.path_for(f"{name}", "err.txt")
        out_f.write_text(stdout, encoding="utf-8")
        err_f.write_text(stderr, encoding="utf-8")
        files = [str(out_f), str(err_f)]
        ctx.calls.append({"tool": name, "argv": argv, "rc": proc.returncode})

    return RunResult(name, argv, proc.returncode, stdout, stderr, duration, files)


# --------------------------------------------------------------------------- #
# 环境探测：编排前先知道哪些工具真装了
# --------------------------------------------------------------------------- #
def probe_tools() -> dict[str, dict]:
    report: dict[str, dict] = {}
    for name, spec in TOOL_REGISTRY.items():
        found = _resolve_binary(spec)
        report[name] = {
            "available": found is not None,
            "path": found,
            "category": spec.category,
            "description": spec.description,
        }
    return report


def print_probe() -> None:
    report = probe_tools()
    ok = sum(1 for v in report.values() if v["available"])
    print(f"工具可用性：{ok}/{len(report)} 已安装\n")
    print(f"{'工具':<12}{'状态':<8}{'说明'}")
    print("-" * 60)
    for name, info in report.items():
        mark = "✓" if info["available"] else "✗"
        print(f"{name:<12}{mark:<8}{info['description']}")
    missing = [n for n, v in report.items() if not v["available"]]
    if missing:
        print(f"\n未安装：{', '.join(missing)}")


if __name__ == "__main__":
    print_probe()
