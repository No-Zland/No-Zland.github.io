# -*- coding: utf-8 -*-
"""给证书墙生成缩略图（WebP），避免直接加载几 MB 的原图。"""
import glob
import hashlib
import io
import json
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POST = os.path.join(ROOT, "content", "post")
OUT = os.path.join(ROOT, "assets", "certs")
MANIFEST = os.path.join(OUT, "manifest.json")
os.makedirs(OUT, exist_ok=True)

EXTS = (".png", ".jpg", ".jpeg", ".webp", ".gif")
files = [f for f in glob.glob(os.path.join(POST, "03-成果展示", "证书", "**", "*"), recursive=True)
         if os.path.isfile(f) and os.path.splitext(f)[1].lower() in EXTS]

manifest = {}
total_before = 0
total_after = 0
for f in sorted(files):
    rel = os.path.relpath(f, POST).replace(os.sep, "/")
    key = hashlib.md5(rel.encode("utf-8")).hexdigest()[:10]
    thumb = key + ".webp"
    dst = os.path.join(OUT, thumb)
    try:
        img = Image.open(f)
        img.load()
    except Exception as e:
        print("skip", rel, e)
        continue
    w, h = img.size
    max_w = 820
    if w > max_w:
        img = img.convert("RGB").resize((max_w, int(h * max_w / w)), Image.LANCZOS)
    else:
        img = img.convert("RGB")
    img.save(dst, "WEBP", quality=80, method=6)
    manifest[rel] = {"thumb": thumb, "w": img.size[0], "h": img.size[1]}
    total_before += os.path.getsize(f)
    total_after += os.path.getsize(dst)

json.dump(manifest, io.open(MANIFEST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("certs:", len(manifest))
print("before %.1f MB -> after %.1f MB" % (total_before / 1048576, total_after / 1048576))
