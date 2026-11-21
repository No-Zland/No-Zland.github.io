# -*- coding: utf-8 -*-
"""编译并运行 tools/nc_gen/<pid>.cpp|py，对拍牛客题目样例。

用法: python tools/verify_solution.py 208614
退出码 0 表示全部样例通过。
"""
import json
import os
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "tools", "nc_gen")
BUILD = os.path.join(GEN, "build")
PROB = os.path.join(ROOT, "tools", "nc_problems")


def norm(s):
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in s.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def main(pid):
    os.makedirs(BUILD, exist_ok=True)
    pj = os.path.join(PROB, f"{pid}.json")
    if not os.path.exists(pj):
        print(f"ERROR: 缺少题面 {pj}")
        return 2
    data = json.load(open(pj, encoding="utf-8"))
    samples = data.get("samples") or []

    cpp = os.path.join(GEN, f"{pid}.cpp")
    py = os.path.join(GEN, f"{pid}.py")
    if os.path.exists(cpp):
        exe = os.path.join(BUILD, f"{pid}.exe")
        cp = subprocess.run(["g++", "-O2", "-std=c++17", "-o", exe, cpp],
                            capture_output=True, text=True)
        if cp.returncode != 0:
            print("COMPILE FAIL")
            print(cp.stderr[:2000])
            return 3
        cmd = [exe]
    elif os.path.exists(py):
        cmd = [sys.executable, py]
    else:
        print(f"ERROR: 缺少代码 tools/nc_gen/{pid}.cpp|py")
        return 2

    if not samples:
        print("WARN: 无样例，跳过运行验证")
        return 0

    ok = 0
    for i, s in enumerate(samples, 1):
        try:
            r = subprocess.run(cmd, input=s.get("input", ""), capture_output=True,
                               text=True, timeout=15, encoding="utf-8", errors="replace")
        except subprocess.TimeoutExpired:
            print(f"样例{i} TIMEOUT")
            continue
        if r.returncode != 0:
            print(f"样例{i} RE exit={r.returncode} {r.stderr[:300]}")
            continue
        if norm(r.stdout) == norm(s.get("output", "")):
            ok += 1
        else:
            print(f"样例{i} WA")
            print("  期望:", repr(norm(s.get("output", "")))[:300])
            print("  实际:", repr(norm(r.stdout))[:300])
    print(f"RESULT {ok}/{len(samples)} passed")
    return 0 if ok == len(samples) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
