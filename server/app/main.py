import hashlib
import hmac
import json
import os
import re
import sqlite3
import subprocess
import threading
import time
from collections import defaultdict, deque
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field

ROOT = Path(os.environ.get("BLOG_ROOT", "/opt/blog")).resolve()
SRC = ROOT / "src"
SITE = ROOT / "site"
POST = SRC / "content" / "post"
DATA = ROOT / "data"
DB_PATH = DATA / "blog.db"
BUILD_PY = SRC / "build_blog.py"
PYTHON = os.environ.get("BLOG_PYTHON", str(ROOT / "venv" / "bin" / "python"))
ADMIN_PASSWORD = os.environ.get("BLOG_ADMIN_PASSWORD", "")
SECRET = os.environ.get("BLOG_SECRET", "")
COOKIE = "blog_session"
SESSION_AGE = 7 * 24 * 3600
BUILD_LOCK = threading.Lock()
LOGIN_ATTEMPTS = defaultdict(deque)

app = FastAPI(title="Blog API", docs_url=None, redoc_url=None, openapi_url=None)


def init_db():
    DATA.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated INTEGER NOT NULL)"
        )
        conn.commit()


init_db()


class LoginBody(BaseModel):
    password: str = Field(min_length=1, max_length=200)


class NoteBody(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    section: str = Field(min_length=1, max_length=80)
    category: str = Field(default="", max_length=80)
    body: str = Field(min_length=1, max_length=200_000)


class TasksBody(BaseModel):
    tasks: list = Field(default_factory=list)


def sign(value: str) -> str:
    return hmac.new(SECRET.encode("utf-8"), value.encode("utf-8"), hashlib.sha256).hexdigest()


def make_session() -> str:
    expires = str(int(time.time()) + SESSION_AGE)
    return expires + "." + sign(expires)


def is_authenticated(request: Request) -> bool:
    token = request.cookies.get(COOKIE, "")
    if "." not in token:
        return False
    expires, signature = token.split(".", 1)
    if not expires.isdigit() or int(expires) < time.time():
        return False
    return hmac.compare_digest(sign(expires), signature)


def require_auth(request: Request) -> None:
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="请先登录服务器")


def safe_name(value: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|#\x00-\x1f]", "", value).strip()
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value[:80]


def run_build() -> str:
    if not BUILD_LOCK.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="正在构建，请稍后再试")
    try:
        result = subprocess.run(
            [PYTHON, str(BUILD_PY), "--clean"],
            cwd=str(SRC),
            capture_output=True,
            text=True,
            timeout=180,
        )
        if result.returncode != 0:
            tail = (result.stderr or result.stdout or "")[-1200:]
            raise HTTPException(status_code=500, detail="构建失败：" + tail)
        return (result.stdout or "").strip()
    finally:
        BUILD_LOCK.release()


@app.get("/api/health")
def health():
    return {"ok": True, "time": int(time.time())}


@app.get("/api/me")
def me(request: Request):
    return {"authenticated": is_authenticated(request)}


@app.post("/api/login")
def login(body: LoginBody, request: Request, response: Response):
    if not ADMIN_PASSWORD or not SECRET:
        raise HTTPException(status_code=503, detail="后端未配置管理员密码")
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    bucket = LOGIN_ATTEMPTS[ip]
    while bucket and now - bucket[0] > 300:
        bucket.popleft()
    if len(bucket) >= 10:
        raise HTTPException(status_code=429, detail="尝试次数过多，请五分钟后再试")
    if not hmac.compare_digest(body.password, ADMIN_PASSWORD):
        bucket.append(now)
        raise HTTPException(status_code=401, detail="密码错误")
    bucket.clear()
    response.set_cookie(
        COOKIE,
        make_session(),
        max_age=SESSION_AGE,
        httponly=True,
        samesite="strict",
        path="/",
    )
    return {"ok": True}


@app.post("/api/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE, path="/")
    return {"ok": True}


@app.post("/api/notes", dependencies=[Depends(require_auth)])
def create_note(body: NoteBody):
    section = safe_name(body.section)
    category = safe_name(body.category)
    title = body.title.strip()
    section_path = POST / section
    if not section or not section_path.is_dir():
        raise HTTPException(status_code=400, detail="板块不存在")
    target_dir = section_path / category if category else section_path
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = (safe_name(title) or "note") + ".md"
    target = target_dir / filename
    markdown = body.body.strip()
    if not markdown.startswith("#"):
        markdown = f"# {title}\n\n{markdown}"
    if not markdown.endswith("\n"):
        markdown += "\n"
    tmp = target.with_suffix(".md.tmp")
    tmp.write_text(markdown, encoding="utf-8")
    os.replace(tmp, target)
    output = run_build()
    return {
        "ok": True,
        "path": str(target.relative_to(SRC)),
        "build": output[-500:],
        "url": "/" + "/".join(p for p in (section, category) if p) + "/index.html",
    }


@app.get("/api/tasks", dependencies=[Depends(require_auth)])
def get_tasks():
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT value FROM settings WHERE key='tasks'").fetchone()
    if not row:
        return {"tasks": []}
    try:
        return {"tasks": json.loads(row[0])}
    except json.JSONDecodeError:
        return {"tasks": []}


@app.put("/api/tasks", dependencies=[Depends(require_auth)])
def put_tasks(body: TasksBody):
    payload = json.dumps(body.tasks, ensure_ascii=False)
    if len(payload.encode("utf-8")) > 1_000_000:
        raise HTTPException(status_code=413, detail="任务数据过大")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO settings(key, value, updated) VALUES('tasks', ?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated=excluded.updated",
            (payload, int(time.time())),
        )
        conn.commit()
    return {"ok": True, "count": len(body.tasks)}
