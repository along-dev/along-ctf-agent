#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PreToolUse hook: warn (never block) when the Agent tool is called with
subagent_type == "general-purpose".

Why: on this machine the API path is Claude Code -> cc-switch -> third-party
relay. That relay intermittently returns stop_reason=="tool_use" with zero
tool_use blocks. Measured: agent type "general-purpose" (large tool set) dies
at its first tool call near 100% of the time; "Explore" (small tool set)
survived 4/4. The operative variable is the tool-set size chosen at dispatch
time. This hook sits at the dispatch layer and advises "Explore" instead.

Contract (PreToolUse):
  stdin  : JSON with session_id, transcript_path, cwd, hook_event_name,
           tool_name, tool_input.
  stdout : JSON {"hookSpecificOutput": {"hookEventName": "PreToolUse",
           "permissionDecision": "allow"}, "systemMessage": "..."} with exit 0
           -> call proceeds AND the message is surfaced.
  exit   : 0 = success/non-blocking. (2 = blocking, we never use it.)

Discipline: warn-only. Every path exits 0. Any error degrades to
allow-with-no-message. No-op for any tool other than Agent and for any
subagent_type other than general-purpose. Safe to run repeatedly.
"""
import json
import os
import sys
import datetime


LOG_NAME = ".agenttype_hook.log"
DANGER = "general-purpose"

WARNING = (
    "[agenttype-warn] Agent dispatched with subagent_type=\"general-purpose\". "
    "On this machine (Claude Code -> cc-switch -> relay) general-purpose "
    "dispatches die at the first tool call near 100% of the time, while "
    "subagent_type=\"Explore\" survived 4/4. Prefer \"Explore\". If the task "
    "needs file writes, Explore can still write via Bash. Proceeding anyway "
    "(warn-only)."
)


def _force_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


def _log(line: str) -> None:
    """Append one line to the log next to this script. Never raise."""
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(here, LOG_NAME)
        ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(ts + " " + line + "\n")
    except Exception:
        pass


def _emit(payload) -> None:
    try:
        sys.stdout.write(json.dumps(payload, ensure_ascii=True))
        sys.stdout.flush()
    except Exception:
        pass


def _run() -> None:
    raw = ""
    try:
        raw = sys.stdin.read()
    except Exception:
        raw = ""

    data = {}
    if raw.strip():
        try:
            data = json.loads(raw)
        except Exception:
            data = {}

    tool_name = ""
    tool_input = {}
    try:
        if isinstance(data, dict):
            tool_name = data.get("tool_name") or ""
            ti = data.get("tool_input")
            if isinstance(ti, dict):
                tool_input = ti
    except Exception:
        tool_name = ""
        tool_input = {}

    subagent_type = ""
    try:
        subagent_type = tool_input.get("subagent_type") or ""
    except Exception:
        subagent_type = ""

    # No-op: anything that is not the exact danger signal.
    if tool_name != "Agent":
        _log("fire tool=%r subagent_type=%r match=no (non-Agent)" % (tool_name, subagent_type))
        return
    if subagent_type != DANGER:
        _log("fire tool=%r subagent_type=%r match=no" % (tool_name, subagent_type))
        return

    # Danger signal: allow, but surface a warning.
    _log("fire tool=%r subagent_type=%r match=YES warn=yes allow=yes" % (tool_name, subagent_type))
    _emit({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": WARNING,
        },
        "systemMessage": WARNING,
    })


def main() -> None:
    _force_utf8()
    try:
        _run()
    except Exception:
        # Never deny, never crash: fall through to a silent allow.
        _log("fire internal-error -> allow-with-no-message")
        return


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
