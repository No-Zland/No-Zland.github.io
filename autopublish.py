# -*- coding: utf-8 -*-
"""
自动发布：盯着 Obsidian 笔记目录，改完静置几秒后自动构建、提交、推送。

用法（在仓库根目录）：

    python autopublish.py            # 常驻监听，Ctrl+C 停止
    python autopublish.py --once     # 立刻跑一轮（有改动就发布）
    python autopublish.py --dry-run  # 只打印将要做什么
    python autopublish.py --no-build # 跳过本地构建校验，直接提交推送

Windows 上双击 autopublish.bat 也能启动。
日志写到 autopublish.log（已被 .gitignore 忽略）。
"""
import argparse
import datetime as dt
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(ROOT, "autopublish.log")

# 只盯这些地方；site/ 是构建产物，盯了会自己触发自己
WATCH_DIRS = [os.path.join(ROOT, "content", "post"), os.path.join(ROOT, "src"), os.path.join(ROOT, "layouts")]
WATCH_FILES = [os.path.join(ROOT, "build_blog.py"), os.path.join(ROOT, "hugo.toml"), os.path.join(ROOT, "requirements.txt")]

SKIP_DIRS = {".git", "site", "public", "resources", "node_modules", "__pycache__", ".obsidian", ".venv", "venv"}
SKIP_SUFFIX = (".tmp", ".log", ".swp", "~")

POLL = 2.0          # 轮询间隔（秒）
QUIET = 8.0         # 最后一次改动后静置多久再发布
PUSH_RETRIES = 5


def log(msg):
    line = "[" + dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] " + msg
    print(line, flush=True)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def snapshot():
    """返回 {路径: (mtime, size)}，用来判断有没有新改动。"""
    state = {}
    for base in WATCH_DIRS:
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            for name in filenames:
                if name.startswith(".") or name.endswith(SKIP_SUFFIX) or name.startswith("~$"):
                    continue
                p = os.path.join(dirpath, name)
                try:
                    st = os.stat(p)
                except OSError:
                    continue
                state[p] = (st.st_mtime_ns, st.st_size)
    for p in WATCH_FILES:
        if os.path.isfile(p):
            st = os.stat(p)
            state[p] = (st.st_mtime_ns, st.st_size)
    return state


def run(cmd, timeout=600):
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, "", "超时（%ss）" % timeout
    out = (proc.stdout or b"").decode("utf-8", "replace").strip()
    err = (proc.stderr or b"").decode("utf-8", "replace").strip()
    return proc.returncode, out, err


def git_changes():
    code, out, _ = run(["git", "status", "--porcelain"])
    if code != 0:
        return []
    return [ln for ln in out.splitlines() if ln.strip()]


def build():
    log("构建中：python build_blog.py --clean")
    code, out, err = run([sys.executable, "build_blog.py", "--clean"])
    if code != 0:
        log("构建失败，跳过本次发布：")
        for ln in (err or out).splitlines()[-12:]:
            log("  " + ln)
        return False
    tail = [ln for ln in out.splitlines() if ln.strip()][-2:]
    for ln in tail:
        log("  " + ln)
    return True


def has_unpushed():
    code, out, _ = run(["git", "rev-list", "--count", "@{u}..HEAD"], timeout=60)
    if code != 0:
        code, out, _ = run(["git", "rev-list", "--count", "origin/HEAD..HEAD"], timeout=60)
    try:
        return int(out.strip() or 0) > 0
    except ValueError:
        return False


def push(do_push=True):
    if not do_push:
        return True
    for attempt in range(1, PUSH_RETRIES + 1):
        code, out, err = run(["git", "push", "origin", "HEAD"], timeout=120)
        if code == 0:
            log("推送成功")
            return True
        last = ((err or out).strip().splitlines() or [""])[-1]
        log("推送失败（第 %d/%d 次）：%s" % (attempt, PUSH_RETRIES, last))
        time.sleep(min(60, 8 * attempt))
    log("推送多次失败，本地提交已保留；后台每 5 分钟再试（或加 --once 手动重试）")
    return False


def publish(message=None, do_build=True, do_push=True):
    changes = git_changes()
    if not changes:
        if has_unpushed():
            log("没有新改动，但有 %s 个本地提交待推送" % "若干")
            return push(do_push)
        log("没有需要提交的改动")
        return True

    if do_build and not build():
        return False

    code, out, err = run(["git", "add", "-A"])
    if code != 0:
        log("git add 失败：" + (err or out))
        return False

    code, out, _ = run(["git", "diff", "--cached", "--numstat"])
    staged = [ln for ln in out.splitlines() if ln.strip()]
    if not staged:
        log("暂存区为空，跳过")
        return push(do_push) if has_unpushed() else True

    if not message:
        message = "auto: %d 个文件 · %s" % (
            len(staged), dt.datetime.now().strftime("%Y-%m-%d %H:%M"))

    code, out, err = run(["git", "-c", "core.quotepath=false", "commit", "-m", message])
    if code != 0:
        log("提交失败：" + (err or out))
        return False
    log("已提交：" + message)

    return push(do_push)


def watch():
    log("开始监听（每 %.0f 秒检查一次，静置 %.0f 秒后发布）" % (POLL, QUIET))
    log("监听目录：" + "、".join(os.path.relpath(d, ROOT) for d in WATCH_DIRS))
    state = snapshot()
    dirty_since = None
    last_push_try = 0.0
    try:
        while True:
            time.sleep(POLL)
            now = snapshot()
            if now != state:
                state = now
                dirty_since = time.time()
                continue
            if dirty_since and time.time() - dirty_since >= QUIET:
                dirty_since = None
                log("检测到改动，准备发布")
                publish()
                last_push_try = time.time()
                continue
            # 之前推送失败（比如断网）的话，后台每 5 分钟补推一次
            if time.time() - last_push_try > 300 and not git_changes() and has_unpushed():
                last_push_try = time.time()
                log("有本地提交没推上去，重试")
                push()
    except KeyboardInterrupt:
        log("已停止监听")


def main():
    ap = argparse.ArgumentParser(description="Obsidian 笔记自动构建并发布到 GitHub")
    ap.add_argument("--once", action="store_true", help="只跑一轮")
    ap.add_argument("--dry-run", action="store_true", help="只显示将要做什么")
    ap.add_argument("--no-build", action="store_true", help="跳过本地构建")
    ap.add_argument("--no-push", action="store_true", help="只提交不推送")
    ap.add_argument("-m", "--message", default=None, help="自定义提交信息")
    args = ap.parse_args()

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        sys.exit("这里不是 git 仓库：" + ROOT)

    if args.dry_run:
        changes = git_changes()
        log("待提交 %d 项；构建检查：%s" % (len(changes), "跳过" if args.no_build else "会执行"))
        for ln in changes[:20]:
            log("  " + ln)
        if len(changes) > 20:
            log("  … 还有 %d 项" % (len(changes) - 20))
        return

    if args.once:
        ok = publish(args.message, do_build=not args.no_build, do_push=not args.no_push)
        sys.exit(0 if ok else 1)

    watch()


if __name__ == "__main__":
    main()
