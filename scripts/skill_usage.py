#!/usr/bin/env python3
"""skill_usage.py — スキルが実際に何回呼ばれたかを、手元の Claude Code の会話ログから数える。

棚卸し（docs/skill_inventory.md）の「使用回数」はこれで測る。git の履歴や成果物からの推定では、
「直した回数」と「使った回数」が混ざるため。

数えるもの（~/.claude/projects/**/*.jsonl）:
  - Skill ツールの呼び出し（モデルが自分で開いた・説明文で自動発動した分）
  - スラッシュコマンドの入力（/zukai など。人が打った分）
同じ呼び出しが resume で複数の jsonl に写っても、tool_use の id / 行の uuid で 1 回に数える。

数えられないもの: cloud セッション（コンテナごと消える）と Codex 側の利用。

  python3 scripts/skill_usage.py                 # 全期間
  python3 scripts/skill_usage.py --since 2026-09-01
  python3 scripts/skill_usage.py --json
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

COMMAND_RE = re.compile(r"<command-name>/?([^<\s]+)</command-name>")
# 組み込みのコマンドはスキルではないので数えない
BUILTIN = {"clear", "compact", "config", "context", "cost", "exit", "help", "init", "login", "logout",
           "mcp", "memory", "model", "permissions", "plugin", "resume", "status", "doctor", "agents",
           "hooks", "ide", "fast", "add-dir", "rewind", "export", "bashes", "usage", "vim", "theme"}


def iter_records(root: Path):
    for path in root.rglob("*.jsonl"):
        try:
            with path.open(encoding="utf-8", errors="replace") as f:
                for line in f:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue
        except OSError:
            continue


def count(root: Path, since: str):
    skills, commands = Counter(), Counter()
    seen = set()
    for rec in iter_records(root):
        if since and rec.get("timestamp", "")[:10] < since:
            continue
        content = (rec.get("message") or {}).get("content")
        if rec.get("type") == "assistant" and isinstance(content, list):
            for part in content:
                if part.get("type") == "tool_use" and part.get("name") == "Skill":
                    key = part.get("id")
                    name = (part.get("input") or {}).get("skill")
                    if name and key not in seen:
                        seen.add(key)
                        skills[name] += 1
        elif rec.get("type") == "user":
            text = content if isinstance(content, str) else " ".join(
                p.get("text", "") for p in content or [] if isinstance(p, dict))
            for name in COMMAND_RE.findall(text):
                key = rec.get("uuid")
                if name not in BUILTIN and (key, name) not in seen:
                    seen.add((key, name))
                    commands[name] += 1
    return skills, commands


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--since", default="", help="YYYY-MM-DD 以降だけ数える")
    ap.add_argument("--root", default=str(Path.home() / ".claude" / "projects"))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    skills, commands = count(Path(a.root), a.since)
    if a.json:
        print(json.dumps({"skills": skills, "commands": commands}, ensure_ascii=False))
        return
    print(f"# 集計元: {a.root}" + (f"（{a.since} 以降）" if a.since else ""))
    for title, c in (("Skill ツールで開かれた回数", skills), ("スラッシュコマンドで打たれた回数", commands)):
        print(f"\n## {title}")
        if not c:
            print("  （記録なし）")
        for name, n in c.most_common():
            print(f"  {n:5d}  {name}")


if __name__ == "__main__":
    main()
