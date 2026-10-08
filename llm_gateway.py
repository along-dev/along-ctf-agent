#!/usr/bin/env python3
"""Project injection layer: inject config/prompt_prefix.yaml prefix/suffix into
the system message before forwarding upstream.

Contract: on_error = passthrough -> unreadable or invalid config means the
original messages are forwarded unchanged. This layer only shapes the project
injection; it cannot change the model's own alignment layer.
"""
import os
import sys

try:
    import yaml
except ImportError:
    yaml = None

DEFAULT_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "prompt_prefix.yaml")


def load_prefix(config_path=DEFAULT_CONFIG):
    if yaml is None or not os.path.isfile(config_path):
        return None
    try:
        cfg = yaml.safe_load(open(config_path, encoding="utf-8")) or {}
    except Exception:
        return None
    if not isinstance(cfg, dict) or not cfg.get("enabled"):
        return None
    if cfg.get("inject_into") != "system":
        return None
    return {
        "prefix": cfg.get("prefix", "") or "",
        "suffix": cfg.get("suffix", "") or "",
        "position": cfg.get("position", "prepend"),
    }


def _join(pre, suf):
    parts = [p for p in (pre.rstrip("\n"), suf.rstrip("\n")) if p]
    return "\n".join(parts)


def inject(messages, block):
    """messages: list of {'role','content'}. Return a new list (input untouched)."""
    if not block:
        return messages
    text = _join(block.get("prefix", ""), block.get("suffix", ""))
    if not text:
        return messages
    out = list(messages)
    for i, m in enumerate(out):
        if isinstance(m, dict) and m.get("role") == "system":
            cur = m.get("content", "") or ""
            merged = (text + "\n" + cur) if block.get("position") == "prepend" else (cur + "\n" + text)
            out[i] = {**m, "content": merged}
            return out
    out.insert(0, {"role": "system", "content": text})
    return out


def forward(messages, config_path=DEFAULT_CONFIG, send=None):
    """Inject then hand off. `send` is the upstream callable; if None, returns the
    injected messages (useful for testing / for callers that do their own POST)."""
    block = load_prefix(config_path)
    injected = inject(messages, block)
    if send is None:
        return injected
    return send(injected)


if __name__ == "__main__":
    import json
    raw = sys.stdin.read()
    try:
        msgs = json.loads(raw) if raw.strip() else []
    except ValueError:
        msgs = [{"role": "user", "content": raw}]
    print(json.dumps(inject(msgs, load_prefix()), ensure_ascii=False, indent=2))
