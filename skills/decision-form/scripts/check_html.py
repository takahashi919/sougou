#!/usr/bin/env python3
"""生成した HTML の <script> を取り出して `node --check` で構文を確かめる。

使い方: python check_html.py out.html   （node が無ければ NG で終わる）
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

page = Path(sys.argv[1]).read_text(encoding="utf-8")
scripts = re.findall(r"<script>(.*?)</script>", page, re.S)
if not scripts:
    sys.exit("NG: <script> が無い")
for i, s in enumerate(scripts):
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as t:
        t.write(s)
    r = subprocess.run(["node", "--check", t.name], capture_output=True, text=True, encoding="utf-8")
    Path(t.name).unlink()
    if r.returncode:
        sys.exit(f"NG: script {i}: {r.stderr.strip()}")
print(f"ok: script {len(scripts)} 個とも node --check を通過")
