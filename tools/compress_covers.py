# -*- coding: utf-8 -*-
"""把书架封面从 PNG 转成 WebP 并压缩宽度，同步更新 manifest。"""
import glob
import io
import json
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "shelf")
MANIFEST = os.path.join(OUT, "manifest.json")

books = json.loads(io.open(MANIFEST, encoding="utf-8").read())
bad = []
saved_before = sum(os.path.getsize(os.path.join(OUT, b["cover"])) for b in books if os.path.exists(os.path.join(OUT, b["cover"])))

for b in books:
    png = os.path.join(OUT, b["cover"].replace(".webp", ".png"))
    webp_name = os.path.splitext(b["cover"])[0] + ".webp"
    webp = os.path.join(OUT, webp_name)
    if not os.path.exists(png):
        if os.path.exists(webp):
            b["cover"] = webp_name
        continue
    try:
        img = Image.open(png).convert("RGB")
    except Exception:
        os.remove(png)
        bad.append(b)
        continue
    w, h = img.size
    target_w = 300
    if w > target_w:
        img = img.resize((target_w, int(h * target_w / w)), Image.LANCZOS)
    img.save(webp, "WEBP", quality=78, method=6)
    b["cover"] = webp_name
    b["w"], b["h"] = img.size
    os.remove(png)

books = [b for b in books if b not in bad]
json.dump(books, io.open(MANIFEST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
saved_after = sum(os.path.getsize(os.path.join(OUT, b["cover"])) for b in books if os.path.exists(os.path.join(OUT, b["cover"])))
print("covers:", len(books))
print("before: %.1f MB  after: %.1f MB" % (saved_before / 1048576, saved_after / 1048576))
