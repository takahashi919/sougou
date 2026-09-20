#!/usr/bin/env python3
"""skills/ を ~/.claude/skills/ へ配る（stdlib のみ、Windows/Linux 共通）。

受付の `skills/` が正本で、`~/.claude/skills/` は**生成コピー**。
symlink は使わない（Windows / Git 互換）。research の sync_skill_mirror.py と同じ作法。

Usage:
    python scripts/sync_user_skills.py --check    # drift を見るだけ（CI 向け・差分ありで exit 1）
    python scripts/sync_user_skills.py --apply    # 配る
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "skills"
DST = Path.home() / ".claude" / "skills"


def _skill_dirs() -> list[Path]:
    if not SRC.exists():
        return []
    return sorted(p for p in SRC.iterdir() if p.is_dir() and (p / "SKILL.md").exists())


def _diff(src: Path, dst: Path) -> list[str]:
    """src にあって dst と違うものを返す。dst 側の余剰は消さない（他の出所があるため）。"""
    out = []
    for s in sorted(p for p in src.rglob("*") if p.is_file()):
        d = dst / s.relative_to(src)
        if not d.exists():
            out.append(f"新規 {s.relative_to(SRC)}")
        elif not filecmp.cmp(s, d, shallow=False):
            out.append(f"変更 {s.relative_to(SRC)}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    skills = _skill_dirs()
    if not skills:
        print(f"skills/ に SKILL.md を持つディレクトリが無い（{SRC}）")
        print("→ skills/README.md を読むこと")
        return 0

    drift: list[str] = []
    for s in skills:
        drift += [f"{s.name}: {line}" for line in _diff(s, DST / s.name)]

    if args.check:
        if drift:
            print(f"drift {len(drift)} 件")
            for d in drift:
                print(f"  {d}")
            return 1
        print(f"[OK] {len(skills)} 本すべて同期済み（drift 0）")
        return 0

    for s in skills:
        target = DST / s.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(s, target, dirs_exist_ok=True)
    print(f"配った: {len(skills)} 本 → {DST}")
    for s in skills:
        print(f"  {s.name}")
    if drift:
        print(f"（うち {len(drift)} 件が新規・変更）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
