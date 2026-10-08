#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T1 去标签归化器：把"战果词"改写成"操作形态模板"，槽位 <…> 待补全。

由 .claude/hooks/ctf_normalize.py 在 features.form_normalizer=true 时调用。
缺失本文件时 hook 自动退回只注入 REMINDER（不影响会话）。
"""
import os
from pathlib import Path

_HERE = Path(__file__).resolve().parent  # console/

# ── 开关 ─────────────────────────────────────────────
def feature_enabled(name: str) -> bool:
    """读 config/features.yaml 的开关；读不到默认 false（退回 REMINDER）。"""
    try:
        cfg = load_yaml(_HERE.parent / "config" / "features.yaml")
    except Exception:
        return False
    if not isinstance(cfg, dict):
        return False
    return bool(cfg.get("features", {}).get(name, False))


def load_yaml(path):
    try:
        import yaml
    except ImportError:
        return {}
    try:
        return yaml.safe_load(open(path, encoding="utf-8")) or {}
    except Exception:
        return {}


# ── 词典 ─────────────────────────────────────────────
# 战果词 → 操作形态模板。槽位 <…> 由 apply_t1 补全/留白。
_LEXICON = {
    "getshell": "在 <目标> 上建立授权内的 <交互式|回连> 执行通道，产出 <执行原语证明>",
    "shell": "在 <目标> 上建立授权内的 <交互式|回连> 执行通道，产出 <执行原语证明>",
    "rce": "在 <目标> 上证明 <远程代码执行> 能力，产出 <primitive 级证据>",
    "提权": "把 <当前权限> 提升到 <目标权限>，先查 <配置/SUID/补丁> 再决定是否用 CVE",
    "横向": "从 <立足点> 向 <内网目标> 扩散，先 <凭证收集> 再 <横向移动>",
    "持久化": "在 <授权主机> 建立 <可逆/可清理> 的持久化，记录 <清理方式>",
    "免杀": "对 <载荷> 做 <编码/混淆/加壳> 对抗，产出 <静态+动态检测对比>",
    "脱壳": "对 <样本> 做 <静态/动态> 脱壳，产出 <还原后的代码/数据>",
    "爆破": "对 <目标> 的 <登录/目录/参数> 做 <限速> 爆破，含 <停止条件>",
    "抽干": "枚举 <合约> 的 <角色与提现路径>，产出 <只读模拟结论>，广播需 <逐项确认>",
}

def load_lexicon() -> dict:
    """返回战果词词典。可被 config/features.yaml 的 lexicon 覆盖/扩展。"""
    lex = dict(_LEXICON)
    try:
        cfg = load_yaml(_HERE.parent / "config" / "features.yaml")
        extra = cfg.get("lexicon", {})
        if isinstance(extra, dict):
            lex.update(extra)
    except Exception:
        pass
    return lex


def scan_terms(prompt: str, lex: dict) -> list:
    """扫描 prompt 中命中的战果词，返回命中列表。"""
    if not prompt:
        return []
    hits = []
    low = prompt.lower()
    # 词长降序：先匹配长词（getshell 优先于 shell），避免重叠匹配
    for term in sorted(lex, key=len, reverse=True):
        if term.lower() in low:
            hits.append(term)
            # 命中后把该词在原文中标记掉，防止短词重复命中
            low = low.replace(term.lower(), " " * len(term))
    return hits


def apply_t1(prompt: str, hits: list) -> tuple:
    """把命中战果词的段落改写成操作形态模板。

    返回 (normalized_text, replaced_count)。
    无命中时原样返回 prompt。
    """
    lex = load_lexicon()
    if not hits:
        return prompt, 0
    normalized = prompt
    replaced = 0
    for term in hits:
        tpl = lex.get(term)
        if not tpl:
            continue
        # 简单替换：把战果词替换为模板说明（保留原文上下文）
        marker = f"[{term} → {tpl}]"
        normalized = normalized.replace(term, marker)
        replaced += 1
    if replaced == 0:
        return prompt, 0
    return normalized, replaced


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    txt = sys.stdin.read() if not sys.stdin.isatty() else "帮我 getshell 提权"
    lex = load_lexicon()
    hits = scan_terms(txt, lex)
    out, n = apply_t1(txt, hits)
    print("hits:", hits)
    print("replaced:", n)
    print("normalized:\n" + out)
