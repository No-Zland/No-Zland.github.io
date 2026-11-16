# -*- coding: utf-8 -*-
"""给每个 PDF 渲染第一页当书封，输出到 assets/shelf/ 并写 manifest.json。"""
import glob
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POST = os.path.join(ROOT, "content", "post")
OUT = os.path.join(ROOT, "assets", "shelf")
PS = os.path.join(ROOT, "tools", "pdfcover.ps1")
os.makedirs(OUT, exist_ok=True)

SHELF_ROOT = os.path.join(POST, "书架")
pdfs = sorted(glob.glob(os.path.join(SHELF_ROOT, "**", "*.pdf"), recursive=True))
manifest = []

for i, path in enumerate(pdfs, 1):
    rel = os.path.relpath(path, POST)
    key = hashlib.md5(rel.encode("utf-8")).hexdigest()[:10]
    cover = key + ".png"
    out = os.path.join(OUT, cover)
    if not os.path.exists(out) and not os.path.exists(os.path.join(OUT, key + ".webp")):
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", PS,
                 "-Pdf", path, "-Out", out, "-Width", "420"],
                capture_output=True, timeout=180,
            )
        except subprocess.TimeoutExpired:
            print("timeout", rel)
    if not os.path.exists(out):
        print("fail", rel)
        continue
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", os.path.join("content", "post", rel)], cwd=ROOT
    ).returncode == 0
    size_mb = round(os.path.getsize(path) / 1048576, 1)
    title = os.path.splitext(os.path.basename(path))[0]
    folder = os.path.dirname(rel).replace(os.sep, " / ")
    manifest.append({
        "title": title,
        "cover": cover,
        "rel": rel.replace(os.sep, "/"),
        "size": size_mb,
        "folder": folder,
        "online": not ignored,
    })
    print("[%d/%d] %s" % (i, len(pdfs), title[:40]))

with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=1)

print("done:", len(manifest), "covers")
