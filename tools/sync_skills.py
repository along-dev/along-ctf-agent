#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 .claude/skills/（Claude Code 加载点）与 skills/（外部副本）之间同步技能。

用法：
  python tools/sync_skills.py                 # 同步 .claude/skills -> skills/（默认方向）
  python tools/sync_skills.py --reverse       # 反向：skills/ -> .claude/skills/
  python tools/sync_skills.py --check         # 只检查是否一致；有差异则 exit 1，不写入
  python tools/sync_skills.py --install-hook  # 安装 pre-commit 钩子（提交前自动同步）

约定：默认以 .claude/skills/ 为准（Claude Code 的工作副本），镜像到 skills/。
镜像 = 复制新增/改动文件，并删除目标端多余文件，使两侧逐字节一致。
"""
import argparse
import filecmp
import os
import shutil
import sys

SKILLS = ("ctf-playbook", "ctf-prompt-optimizer", "redteam-agent")


def _repo_root() -> str:
    # tools/sync_skills.py -> 仓库根 = tools 的上一级
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _diff_dirs(a: str, b: str):
    """返回 (仅a有, 仅b有, 内容不同) 三组相对路径。"""
    def rels(base):
        out = set()
        for dirpath, _dirs, files in os.walk(base):
            for f in files:
                out.add(os.path.relpath(os.path.join(dirpath, f), base))
        return out

    if not os.path.isdir(a) and not os.path.isdir(b):
        return set(), set(), set()
    if not os.path.isdir(a):
        return set(), rels(b), set()
    if not os.path.isdir(b):
        return rels(a), set(), set()

    ra, rb = rels(a), rels(b)
    only_a = ra - rb
    only_b = rb - ra
    changed = {
        r for r in (ra & rb)
        if not filecmp.cmp(os.path.join(a, r), os.path.join(b, r), shallow=False)
    }
    return only_a, only_b, changed


def _mirror(src: str, dst: str) -> int:
    """使 dst 与 src 逐字节一致（复制改动 + 删除多余）。返回改动文件数。"""
    only_src, only_dst, changed = _diff_dirs(src, dst)
    n = 0
    for r in sorted(only_dst):
        os.remove(os.path.join(dst, r))
        n += 1
    for r in sorted(only_src | changed):
        s, d = os.path.join(src, r), os.path.join(dst, r)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)
        n += 1
    return n


def _install_hook(root: str) -> int:
    hooks_dir = os.path.join(root, ".git", "hooks")
    if not os.path.isdir(hooks_dir):
        print("找不到 .git/hooks，跳过钩子安装", file=sys.stderr)
        return 1
    hook = os.path.join(hooks_dir, "pre-commit")
    body = (
        "#!/bin/sh\n"
        "# 提交前自动同步技能两份副本（由 tools/sync_skills.py --install-hook 生成）\n"
        "python \"$(git rev-parse --show-toplevel)/tools/sync_skills.py\" || exit 1\n"
        "git add -- .claude/skills skills\n"
        "exit 0\n"
    )
    with open(hook, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    try:
        os.chmod(hook, 0o755)
    except OSError:
        pass
    print("已安装 pre-commit 钩子：", hook)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="同步技能两份副本")
    ap.add_argument("--reverse", action="store_true", help="反向：skills/ -> .claude/skills/")
    ap.add_argument("--check", action="store_true", help="只检查一致性，不写入")
    ap.add_argument("--install-hook", action="store_true", help="安装 pre-commit 钩子")
    args = ap.parse_args()

    root = _repo_root()
    if args.install_hook:
        return _install_hook(root)

    src = os.path.join(root, "skills" if args.reverse else os.path.join(".claude", "skills"))
    dst = os.path.join(root, ".claude" if args.reverse else "", "skills")

    total = 0
    drift = False
    for name in SKILLS:
        s, d = os.path.join(src, name), os.path.join(dst, name)
        only_s, only_d, changed = _diff_dirs(s, d)
        if only_s or only_d or changed:
            drift = True
            if args.check:
                print("漂移 | %s：仅源有 %d，仅目标有 %d，内容不同 %d"
                      % (name, len(only_s), len(only_d), len(changed)))
            else:
                n = _mirror(s, d)
                total += n
                print("同步 | %s：%d 个文件" % (name, n))
        else:
            print("一致 | %s" % name)

    if args.check:
        return 1 if drift else 0
    print("完成，共改动 %d 个文件（%s -> %s）" % (total, src, dst))
    return 0


if __name__ == "__main__":
    sys.exit(main())
