# -*- coding: utf-8 -*-
"""抓取牛客竞赛个人练习记录（服务端渲染 HTML，无需登录）。"""
import json
import re
import sys
import time
import urllib.request

BASE = "https://ac.nowcoder.com/acm/contest/profile/185554642/practice-coding"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

TR_RE = re.compile(r"<tr>(.*?)</tr>", re.S)
SUB_RE = re.compile(r"view-submission\?submissionId=(\d+)")
PROB_RE = re.compile(r'href="/acm/problem/(\d+)"[^>]*>([^<]+)</a>')
RESULT_RE = re.compile(r'<td><a[^>]*class="([^"]*)"[^>]*>([^<]+)</a></td>')
SCORE_RE = re.compile(r'match-score\d+">(\d+)</span>')
TD_RE = re.compile(r"<td>(.*?)</td>", re.S)


def strip(s):
    return re.sub(r"<[^>]+>", "", s).strip()


def fetch(page):
    url = f"{BASE}?page={page}&pageSize=100&statusTypeFilter=-1&orderType=DESC"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def parse(html):
    rows = []
    for tr in TR_RE.findall(html):
        sub = SUB_RE.search(tr)
        prob = PROB_RE.search(tr)
        if not sub or not prob:
            continue
        tds = [strip(x) for x in TD_RE.findall(tr)]
        result = RESULT_RE.search(tr)
        rows.append({
            "submissionId": int(sub.group(1)),
            "problemId": int(prob.group(1)),
            "title": prob.group(2).strip(),
            "result": result.group(2).strip() if result else "",
            "score": tds[3] if len(tds) > 3 else "",
            "timeMs": tds[4] if len(tds) > 4 else "",
            "memoryKb": tds[5] if len(tds) > 5 else "",
            "codeLen": tds[6] if len(tds) > 6 else "",
            "language": tds[7] if len(tds) > 7 else "",
            "submitTime": tds[8] if len(tds) > 8 else "",
        })
    return rows


def main():
    all_rows = []
    for page in range(1, 30):
        html = fetch(page)
        rows = parse(html)
        if not rows:
            break
        all_rows.extend(rows)
        print(f"page {page}: {len(rows)} rows", file=sys.stderr)
        time.sleep(0.4)
    # 去重（同一 submission 只出现一次），按提交时间倒序
    seen = set()
    uniq = []
    for r in all_rows:
        if r["submissionId"] in seen:
            continue
        seen.add(r["submissionId"])
        uniq.append(r)
    out = "tools/nc_submissions.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(uniq, f, ensure_ascii=False, indent=1)
    print(f"total {len(uniq)} submissions -> {out}")


if __name__ == "__main__":
    main()
