"""tools 包：红队工具调用层。

上层编排只依赖这里的函数，不直接调用 subprocess。
"""

from .base import RunContext, RunResult, TOOL_REGISTRY, run_tool, probe_tools, print_probe
from . import recon, scanner, report

__all__ = [
    "RunContext", "RunResult", "TOOL_REGISTRY", "run_tool",
    "probe_tools", "print_probe", "recon", "scanner", "report",
]
