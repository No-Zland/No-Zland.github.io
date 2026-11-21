# -*- coding: utf-8 -*-
"""校验洛谷题号与标题，输出可用题池。"""
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding="utf-8")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

IDS = """P1046 P1980 P1553 P1328 P1094 P1223 P1803 P5019 P1090 P1255 P1044 P1028 P1464
P1115 P2367 P3397 P2004 P1102 P1147 P1638 P2249 P2678 P1182 P2440 P3853 P1024
P1601 P1303 P1045 P1100 P1449 P1739 P1886 P5788 P3378 P3367 P1551 P2024 P1525
P5318 P3916 P4017 P1113 P1807 P3371 P4779 P1339 P1119 P3385 P3366 P1546 P1195
P3379 P1352 P1122 P3128 P3258 P3383 P1226 P3811 P1082 P4549 P1495 P2822 P3807
P2197 P1247 P1216 P1048 P1616 P1060 P1049 P1020 P1091 P1280 P1439 P1541 P1880
P1063 P1004 P2014 P1879 P1896 P2602 P2657 P3375 P3370 P2580 P8306 P1067 P1563""".split()


def get(pid):
    try:
        req = urllib.request.Request(f"https://www.luogu.com.cn/problem/{pid}",
                                     headers={"User-Agent": UA})
        h = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
        t = re.search(r"<title>(.*?)</title>", h)
        return pid, (t.group(1).replace(" - 洛谷", "").strip() if t else "")
    except Exception as e:
        return pid, f"ERR {e}"


with ThreadPoolExecutor(max_workers=5) as ex:
    res = list(ex.map(get, IDS))
for pid, title in res:
    print(pid, title)
json.dump(dict(res), open("tools/luogu_titles.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
