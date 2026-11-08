# 08 · 服务端：FastAPI、SQLite 与部署

> 所属：《念安 TOUCHMIND · 开发文档（全量代码复现版）》  
> 路径基准：仓库根目录 `TOUGHMIND/`，本文所有文件均以**相对路径**标记。

服务端提供账号、关心组、设备、位置、打卡、日程、提醒、留言、轻推与大模型转发，并带 30 天数据清理与最低版本门禁。本篇按 config/security/db/schemas/routers 的拆分顺序写入。

## 本篇复现顺序

| 步骤 | 内容 | 文件数 |
|---|---|---|
| [1. 应用与路由模块](#s08-1) | `app/main.py` 只负责装配：创建 FastAPI、挂版本中间件、注册路由与启动清理任务；业务按领域分布在 `app/routers/`。 | 20 |
| [2. 容器与部署脚本](#s08-2) | Dockerfile 以 uvicorn 启动 `app.main:app`；compose 同时编排 EMQX、backend 与 Ollama。 | 4 |
| [3. 后端接口测试](#s08-3) | 用 FastAPI TestClient 覆盖关心组、设备绑定与成员管理流程。 | 3 |

本篇共 **3 个步骤 / 27 个文件**，按表格顺序写入即可还原对应代码。

<a id="s08-1"></a>

## 步骤 08.1 · 应用与路由模块

`app/main.py` 只负责装配：创建 FastAPI、挂版本中间件、注册路由与启动清理任务；业务按领域分布在 `app/routers/`。

本步骤涉及的文件：

- `server/backend/app/__init__.py`
- `server/backend/app/config.py`
- `server/backend/app/db.py`
- `server/backend/app/helpers.py`
- `server/backend/app/main.py`
- `server/backend/app/routers/__init__.py`
- `server/backend/app/routers/auth.py`
- `server/backend/app/routers/checkins.py`
- `server/backend/app/routers/devices.py`
- `server/backend/app/routers/groups.py`
- `server/backend/app/routers/health.py`
- `server/backend/app/routers/llm.py`
- `server/backend/app/routers/messages.py`
- `server/backend/app/routers/nudge.py`
- `server/backend/app/routers/presence.py`
- `server/backend/app/routers/reminders.py`
- `server/backend/app/routers/schedule.py`
- `server/backend/app/routers/tasks.py`
- `server/backend/app/schemas.py`
- `server/backend/app/security.py`

### `server/backend/app/__init__.py`

````python

````

### `server/backend/app/config.py`

> 环境变量与业务常量（版本门禁、在线窗口、成员上限、保留天数、密钥）。

````python
"""念安后端运行配置：环境变量与服务端常量。"""

import os

DB_PATH = os.environ.get("DB_PATH", "/data/care.db")

LLM_UPSTREAM_URL = os.environ.get("LLM_UPSTREAM_URL", "").strip()

LLM_UPSTREAM_API_KEY = os.environ.get("LLM_UPSTREAM_API_KEY", "").strip()

LLM_MODEL = os.environ.get("LLM_MODEL", "qwen2.5:3b").strip()

APP_VERSION = "5.0.1"

MIN_APP_VERSION = (5, 0, 1)

ONLINE_WINDOW_SECONDS = 120

MAX_GROUP_MEMBERS = 2

MAX_GROUP_DEVICES = 4

INVITE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

DEVICE_JOIN_SECRET = os.environ.get(
    "DEVICE_JOIN_SECRET", "toughmind_dms_hmac_key_2025"
).strip()

DEVICE_ACCOUNT_PREFIX = "device:"

GROUP_AES_SECRET = os.environ.get(
    "GROUP_AES_KEY", "toughmind-group-aes-key-2026"
).strip()

DEVICE_CODE_KEY = os.environ.get(
    "DEVICE_CODE_KEY", "toughmind-device-code-2026"
).strip()

RETENTION_DAYS = 30
````

### `server/backend/app/db.py`

> SQLite 连接、建表、迁移与 30 天数据清理。

````python
"""SQLite 连接、建表迁移与历史数据清理。"""

import os
import sqlite3
import time
from datetime import date as date_cls, timedelta

from .config import DB_PATH, RETENTION_DAYS

def _connect() -> sqlite3.Connection:
    directory = os.path.dirname(DB_PATH)
    if directory:
        os.makedirs(directory, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _init_db() -> None:
    conn = _connect()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account TEXT NOT NULL UNIQUE,
            nickname TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            token TEXT NOT NULL,
            avatar_base64 TEXT NOT NULL DEFAULT '',
            active_group_id INTEGER NOT NULL DEFAULT 0,
            created_at INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS care_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invite_code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL DEFAULT '关心组',
            join_password TEXT NOT NULL DEFAULT '',
            created_by TEXT NOT NULL,
            created_at INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS care_members (
            group_id INTEGER NOT NULL,
            account TEXT NOT NULL,
            relation TEXT NOT NULL DEFAULT '家人',
            role TEXT NOT NULL DEFAULT 'member',
            joined_at INTEGER NOT NULL,
            PRIMARY KEY (group_id, account)
        );

        CREATE TABLE IF NOT EXISTS join_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            account TEXT NOT NULL,
            relation TEXT NOT NULL DEFAULT '家人',
            status TEXT NOT NULL DEFAULT 'pending',
            created_at INTEGER NOT NULL,
            reviewed_at INTEGER NOT NULL DEFAULT 0,
            reviewed_by TEXT NOT NULL DEFAULT '',
            UNIQUE (group_id, account)
        );

        -- ESP32 等硬件设备作为「设备成员」加入关心组，不占用两人名额。
        CREATE TABLE IF NOT EXISTS group_devices (
            group_id INTEGER NOT NULL,
            device_id TEXT NOT NULL,
            name TEXT NOT NULL DEFAULT '',
            relation TEXT NOT NULL DEFAULT '家人',
            added_by TEXT NOT NULL,
            added_at INTEGER NOT NULL,
            token TEXT NOT NULL DEFAULT '',
            PRIMARY KEY (group_id, device_id)
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_group_devices_device
            ON group_devices(device_id);

        CREATE TABLE IF NOT EXISTS presence (
            account TEXT PRIMARY KEY,
            lat REAL NOT NULL DEFAULT 0,
            lon REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'UNKNOWN',
            activity_note TEXT NOT NULL DEFAULT '',
            battery INTEGER NOT NULL DEFAULT -1,
            device_type TEXT NOT NULL DEFAULT 'PHONE',
            mood_emoji TEXT NOT NULL DEFAULT '🙂',
            mood_message TEXT NOT NULL DEFAULT '',
            updated_at INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS check_ins (
            date TEXT NOT NULL,
            account TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            updated_at INTEGER NOT NULL,
            PRIMARY KEY (date, account)
        );

        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time_minutes INTEGER NOT NULL,
            title TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            enabled INTEGER NOT NULL DEFAULT 1,
            created_by TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS nudges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            from_account TEXT NOT NULL,
            to_account TEXT NOT NULL,
            message TEXT NOT NULL DEFAULT '',
            created_at INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS schedule_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            author TEXT NOT NULL,
            date TEXT NOT NULL,
            time_minutes INTEGER NOT NULL DEFAULT 0,
            content TEXT NOT NULL DEFAULT '',
            image_base64 TEXT NOT NULL DEFAULT '',
            created_at INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS checkin_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            title TEXT NOT NULL,
            image_base64 TEXT NOT NULL DEFAULT '',
            creator TEXT NOT NULL,
            done_creator INTEGER NOT NULL DEFAULT 0,
            done_other INTEGER NOT NULL DEFAULT 0,
            created_at INTEGER NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_check_ins_date ON check_ins(date);
        CREATE INDEX IF NOT EXISTS idx_reminders_group_date ON reminders(group_id, date);
        CREATE INDEX IF NOT EXISTS idx_nudges_to ON nudges(to_account, id);
        CREATE INDEX IF NOT EXISTS idx_schedule_group_date ON schedule_posts(group_id, date);

        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            from_account TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_chat_group_id ON chat_messages(group_id, id);
        """
    )
    # 轻量迁移：为已有数据库补充新列
    presence_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(presence)").fetchall()
    }
    if "mood_emoji" not in presence_columns:
        conn.execute(
            "ALTER TABLE presence ADD COLUMN mood_emoji TEXT NOT NULL DEFAULT '🙂'"
        )
    if "mood_message" not in presence_columns:
        conn.execute(
            "ALTER TABLE presence ADD COLUMN mood_message TEXT NOT NULL DEFAULT ''"
        )
    user_columns = {row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
    if "avatar_base64" not in user_columns:
        conn.execute("ALTER TABLE users ADD COLUMN avatar_base64 TEXT NOT NULL DEFAULT ''")
    if "active_group_id" not in user_columns:
        conn.execute("ALTER TABLE users ADD COLUMN active_group_id INTEGER NOT NULL DEFAULT 0")

    group_columns = {row[1] for row in conn.execute("PRAGMA table_info(care_groups)").fetchall()}
    if "name" not in group_columns:
        conn.execute("ALTER TABLE care_groups ADD COLUMN name TEXT NOT NULL DEFAULT '关心组'")
    if "join_password" not in group_columns:
        conn.execute("ALTER TABLE care_groups ADD COLUMN join_password TEXT NOT NULL DEFAULT ''")

    # v5.0.1：一个账号可以加入多个关心组，移除旧的 UNIQUE(account)。
    member_sql_row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='care_members'"
    ).fetchone()
    member_sql = (member_sql_row["sql"] if member_sql_row else "") or ""
    if "UNIQUE (account)" in member_sql.upper():
        conn.executescript(
            """
            ALTER TABLE care_members RENAME TO care_members_old;
            CREATE TABLE care_members (
                group_id INTEGER NOT NULL,
                account TEXT NOT NULL,
                relation TEXT NOT NULL DEFAULT '家人',
                role TEXT NOT NULL DEFAULT 'member',
                joined_at INTEGER NOT NULL,
                PRIMARY KEY (group_id, account)
            );
            INSERT OR IGNORE INTO care_members (group_id, account, relation, role, joined_at)
                SELECT group_id, account, relation, role, joined_at FROM care_members_old;
            DROP TABLE care_members_old;
            """
        )
    reminder_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(reminders)").fetchall()
    }
    if "type" not in reminder_columns:
        conn.execute(
            "ALTER TABLE reminders ADD COLUMN type TEXT NOT NULL DEFAULT 'schedule'"
        )
    check_in_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(check_ins)").fetchall()
    }
    if "goal" not in check_in_columns:
        conn.execute(
            "ALTER TABLE check_ins ADD COLUMN goal TEXT NOT NULL DEFAULT ''"
        )
    if "image_base64" not in check_in_columns:
        conn.execute(
            "ALTER TABLE check_ins ADD COLUMN image_base64 TEXT NOT NULL DEFAULT ''"
        )
    conn.commit()
    conn.close()


_init_db()


def _purge_old_data() -> None:
    """只保留最近 30 天的日志、日程、打卡、提醒与消息。"""
    conn = _connect()
    try:
        cutoff_date = (date_cls.today() - timedelta(days=RETENTION_DAYS)).isoformat()
        cutoff_epoch = int(time.time()) - RETENTION_DAYS * 24 * 3600
        for table in ("schedule_posts", "check_ins", "reminders", "checkin_tasks"):
            conn.execute(f"DELETE FROM {table} WHERE date < ?", (cutoff_date,))
        conn.execute("DELETE FROM nudges WHERE created_at < ?", (cutoff_epoch,))
        conn.execute("DELETE FROM chat_messages WHERE created_at < ?", (cutoff_epoch,))
        # 清理历史重复消息（同组、同发送者、同内容、同秒），避免账号收到重复消息。
        conn.execute(
            """
            DELETE FROM chat_messages WHERE id NOT IN (
                SELECT MIN(id) FROM chat_messages
                GROUP BY group_id, from_account, message, created_at
            )
            """
        )
        conn.execute(
            """
            DELETE FROM nudges WHERE id NOT IN (
                SELECT MIN(id) FROM nudges
                GROUP BY group_id, from_account, to_account, message, created_at
            )
            """
        )
        conn.execute(
            "DELETE FROM presence WHERE updated_at > 0 AND updated_at < ?",
            (cutoff_epoch,),
        )
        conn.commit()
    finally:
        conn.close()
````

### `server/backend/app/helpers.py`

> 组成员/设备/在线状态的组装与距离计算等纯函数。

````python
"""关心组、成员、设备与位置相关的公共函数。"""

import math
import secrets
import sqlite3
import time
from datetime import date as date_cls
from typing import List, Optional

from fastapi import HTTPException

from .config import DEVICE_ACCOUNT_PREFIX, INVITE_ALPHABET, ONLINE_WINDOW_SECONDS

def _nickname_of(account: str) -> str:
    return "用户" + (account[-4:] if len(account) >= 4 else account)


def _group_row(
    conn: sqlite3.Connection, account: str, group_id: Optional[int] = None
) -> Optional[sqlite3.Row]:
    """返回指定组，或当前账号的 active group（兼容旧数据的最近加入组）。"""
    base = """
        SELECT g.id, g.invite_code, g.name, g.join_password,
               g.created_by, g.created_at,
               m.relation, m.role, m.joined_at
        FROM care_groups g
        JOIN care_members m ON m.group_id = g.id
        WHERE m.account = ?
    """
    if group_id is not None:
        return conn.execute(base + " AND g.id = ?", (account, group_id)).fetchone()
    active = conn.execute(
        "SELECT active_group_id FROM users WHERE account = ?", (account,)
    ).fetchone()
    if active is not None and int(active["active_group_id"] or 0) > 0:
        row = conn.execute(
            base + " AND g.id = ?",
            (account, int(active["active_group_id"])),
        ).fetchone()
        if row is not None:
            return row
    return conn.execute(
        base + " ORDER BY m.joined_at DESC LIMIT 1", (account,)
    ).fetchone()


def _set_active_group(conn: sqlite3.Connection, account: str, group_id: int) -> None:
    conn.execute(
        "UPDATE users SET active_group_id = ? WHERE account = ?", (group_id, account)
    )


def _group_count(conn: sqlite3.Connection, group_id: int) -> int:
    return conn.execute(
        "SELECT COUNT(*) AS c FROM care_members WHERE group_id = ?", (group_id,)
    ).fetchone()["c"]


def _new_invite_code(conn: sqlite3.Connection) -> str:
    for _ in range(30):
        code = "".join(secrets.choice(INVITE_ALPHABET) for _ in range(6))
        exists = conn.execute(
            "SELECT 1 FROM care_groups WHERE invite_code = ?", (code,)
        ).fetchone()
        if not exists:
            return code
    raise HTTPException(status_code=500, detail="邀请码生成失败，请重试")


def _presence_payload(row: Optional[sqlite3.Row]) -> Optional[dict]:
    if row is None:
        return None
    age = int(time.time()) - int(row["updated_at"])
    return {
        "lat": row["lat"],
        "lon": row["lon"],
        "status": row["status"],
        "activity_note": row["activity_note"],
        "battery": row["battery"],
        "device_type": row["device_type"],
        "mood_emoji": row["mood_emoji"],
        "mood_message": row["mood_message"],
        "updated_at": row["updated_at"],
        "online": age <= ONLINE_WINDOW_SECONDS,
        "age_seconds": max(0, age),
    }


def _member_payload(
    conn: sqlite3.Connection, row: sqlite3.Row, viewer: str
) -> dict:
    presence = _presence_payload(
        conn.execute(
            "SELECT * FROM presence WHERE account = ?", (row["account"],)
        ).fetchone()
    )
    return {
        "account": row["account"],
        "nickname": row["nickname"] or _nickname_of(row["account"]),
        "relation": row["relation"],
        "role": row["role"],
        "joined_at": row["joined_at"],
        "is_self": row["account"] == viewer,
        "is_device": False,
        "presence": presence,
    }


def _device_account(device_id: str) -> str:
    return f"{DEVICE_ACCOUNT_PREFIX}{device_id}"


def _device_presence(conn: sqlite3.Connection, device_id: str) -> Optional[dict]:
    return _presence_payload(
        conn.execute(
            "SELECT * FROM presence WHERE account = ?",
            (_device_account(device_id),),
        ).fetchone()
    )


def _device_member_payload(
    conn: sqlite3.Connection, row: sqlite3.Row, me: Optional[dict] = None
) -> dict:
    """把 group_devices 的一行转成与 care_members 成员同构的成员对象。"""
    presence = _device_presence(conn, row["device_id"])
    member = {
        "account": _device_account(row["device_id"]),
        "device_id": row["device_id"],
        "nickname": (row["name"] or "").strip() or row["device_id"],
        "relation": row["relation"] or "设备",
        "role": "device",
        "joined_at": row["added_at"],
        "is_self": False,
        "is_device": True,
        "added_by": row["added_by"],
        "presence": presence,
    }
    if me is not None:
        member["distance_m"] = _distance_between_presence(me, member)
    return member


def _group_devices(
    conn: sqlite3.Connection,
    group_id: int,
    me: Optional[dict] = None,
) -> List[dict]:
    rows = conn.execute(
        "SELECT * FROM group_devices WHERE group_id = ? ORDER BY added_at ASC",
        (group_id,),
    ).fetchall()
    return [_device_member_payload(conn, row, me) for row in rows]


def _group_payload(
    conn: sqlite3.Connection,
    account: str,
    group: Optional[sqlite3.Row] = None,
    pending: bool = False,
) -> dict:
    if group is None:
        group = _group_row(conn, account)
    if group is None:
        return {
            "in_group": False,
            "pending": pending,
            "message": "",
            "group": None,
            "me": None,
            "members": [],
            "devices": [],
            "partner": None,
            "requests": [],
        }
    members = [
        _member_payload(conn, row, account)
        for row in conn.execute(
            """
            SELECT m.account, m.relation, m.role, m.joined_at, u.nickname
            FROM care_members m
            LEFT JOIN users u ON u.account = m.account
            WHERE m.group_id = ?
            ORDER BY m.joined_at ASC
            """,
            (group["id"],),
        ).fetchall()
    ]
    me = next((m for m in members if m["account"] == account), None)
    devices = _group_devices(conn, group["id"], me)
    members.extend(devices)
    # 手机才是「TA」：设备成员不能抢占 partner 的位置。
    partner = next(
        (
            m
            for m in members
            if m["account"] != account and not m.get("is_device")
        ),
        None,
    )
    if partner is not None:
        partner["distance_m"] = _distance_between_presence(me, partner)
    requests = []
    if me is not None and me.get("role") == "owner":
        requests = [
            {
                "id": row["id"],
                "account": row["account"],
                "nickname": row["nickname"] or row["account"],
                "relation": row["relation"],
                "created_at": row["created_at"],
            }
            for row in conn.execute(
                """
                SELECT r.id, r.account, r.relation, r.created_at, u.nickname
                FROM join_requests r
                LEFT JOIN users u ON u.account = r.account
                WHERE r.group_id = ? AND r.status = 'pending'
                ORDER BY r.created_at ASC
                """,
                (group["id"],),
            ).fetchall()
        ]
    return {
        "in_group": me is not None,
        "pending": pending,
        "message": "",
        "group": {
            "id": group["id"],
            "invite_code": group["invite_code"],
            "name": group["name"] or "关心组",
            "created_by": group["created_by"],
            "created_at": group["created_at"],
            "role": me.get("role") if me else "",
            "has_password": bool(group["join_password"]),
            "member_count": _group_count(conn, group["id"]),
            "device_count": len(devices),
            "pending_count": len(requests),
        },
        "me": me,
        "members": members,
        "devices": devices,
        "partner": partner,
        "requests": requests,
    }


def _distance_between_presence(me: Optional[dict], partner: Optional[dict]) -> Optional[float]:
    if not me or not partner:
        return None
    a, b = me.get("presence"), partner.get("presence")
    if not a or not b:
        return None
    if not _valid_position(a["lat"], a["lon"]) or not _valid_position(b["lat"], b["lon"]):
        return None
    return round(_distance_m(a["lat"], a["lon"], b["lat"], b["lon"]), 1)


def _valid_position(lat: float, lon: float) -> bool:
    return abs(lat) > 0.000001 or abs(lon) > 0.000001


def _distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6_371_000.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    )
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _parse_date(value: str) -> str:
    try:
        return date_cls.fromisoformat(value).isoformat()
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式应为 yyyy-MM-dd")
````

### `server/backend/app/main.py`

> FastAPI 装配入口：创建应用、挂版本中间件、注册路由与启动 30 天清理任务。

````python
"""念安 · 后端服务

提供：
  1. 用户鉴权（注册 / 登录），数据存 SQLite，密码 PBKDF2-SHA256 加盐哈希，返回不透明 Token。
  2. 亲友关心组：创建邀请码、加入、退出、成员信息。
  3. 双方状态：手机 / ESP32 上报位置、电量、状态；对方可读取。
  4. 双人打卡：双方打卡记录云端同步。
  5. 共享提醒：关心组内共享的日历提醒。
  6. 关心消息：点击「轻轻提醒 TA」后写入云端，对方轮询获取。
  7. OpenAI 兼容的大模型代理（/v1/chat/completions）；未配置上游时返回规则化建议。

环境变量：
  DB_PATH                 SQLite 数据库路径（默认 /data/care.db）
  LLM_UPSTREAM_URL        OpenAI 兼容接口完整地址（可选）
  LLM_UPSTREAM_API_KEY    上游大模型密钥（可选）
"""

import asyncio

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import APP_VERSION, MIN_APP_VERSION
from .db import _purge_old_data
from .routers import (
    auth,
    checkins,
    devices,
    groups,
    health,
    llm,
    messages,
    nudge,
    presence,
    reminders,
    schedule,
    tasks,
)

app = FastAPI(title="念安后端", version=APP_VERSION)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _version_tuple(value: str) -> tuple:
    parts = []
    for piece in value.strip().split("."):
        if not piece.isdigit():
            break
        parts.append(int(piece))
    return tuple(parts or [0])


@app.middleware("http")
async def enforce_app_version(request: Request, call_next):
    """5.0.1 起只接受新版 App；旧版本无法再读写关心组数据。

    ESP32 的 /api/care/devices/* 使用 device_secret / X-Device-Token，
    没有 App 版本号，单独放行。
    """
    path = request.url.path
    if path.startswith("/api/") and not path.startswith("/api/care/devices/"):
        version = request.headers.get("x-app-version", "")
        if _version_tuple(version) < MIN_APP_VERSION:
            return JSONResponse(
                status_code=426,
                content={
                    "detail": "当前客户端版本过低，请升级到 5.0.1 后再使用",
                    "min_version": APP_VERSION,
                },
            )
    return await call_next(request)


@app.on_event("startup")
async def _start_retention_worker() -> None:
    _purge_old_data()

    async def loop() -> None:
        while True:
            await asyncio.sleep(6 * 3600)
            try:
                _purge_old_data()
            except Exception:
                pass

    asyncio.create_task(loop())


app.include_router(auth.router)
app.include_router(health.router)
app.include_router(groups.router)
app.include_router(devices.router)
app.include_router(presence.router)
app.include_router(checkins.router)
app.include_router(tasks.router)
app.include_router(schedule.router)
app.include_router(messages.router)
app.include_router(reminders.router)
app.include_router(nudge.router)
app.include_router(llm.router)
````

### `server/backend/app/routers/__init__.py`

````python

````

### `server/backend/app/routers/auth.py`

> 注册与登录。

````python
"""鉴权、登录与个人资料接口。"""

import secrets
import time
from typing import Optional

from fastapi import APIRouter, Header, HTTPException

from ..db import _connect
from ..helpers import _group_row, _nickname_of
from ..schemas import AuthRequest, AuthResponse, ProfileRequest
from ..security import _hash_password, _require_user, _verify_password

router = APIRouter()

@router.post("/api/auth/register", response_model=AuthResponse)
def register(req: AuthRequest):
    account = req.account.strip()
    if not account:
        raise HTTPException(status_code=400, detail="账号不能为空")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="密码长度至少 6 位")

    conn = _connect()
    try:
        exists = conn.execute(
            "SELECT 1 FROM users WHERE account = ?", (account,)
        ).fetchone()
        if exists:
            raise HTTPException(status_code=409, detail="账号已存在")

        token = secrets.token_hex(32)
        nickname = _nickname_of(account)
        conn.execute(
            "INSERT INTO users (account, nickname, password_hash, token, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (account, nickname, _hash_password(req.password), token, int(time.time())),
        )
        conn.commit()
        return AuthResponse(account=account, nickname=nickname, token=token, avatar_base64="")
    finally:
        conn.close()


@router.post("/api/auth/login", response_model=AuthResponse)
def login(req: AuthRequest):
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE account = ?", (req.account.strip(),)
        ).fetchone()
        if row is None or not _verify_password(req.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="账号或密码错误")
        return AuthResponse(
            account=row["account"],
            nickname=row["nickname"],
            token=row["token"],
            avatar_base64=row["avatar_base64"] or "",
        )
    finally:
        conn.close()


@router.put("/api/care/profile")
def update_profile(req: ProfileRequest, authorization: Optional[str] = Header(default=None)):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        account = user["account"]
        now = int(time.time())
        if req.nickname is not None and req.nickname.strip():
            conn.execute(
                "UPDATE users SET nickname = ? WHERE account = ?",
                (req.nickname.strip(), account),
            )
        group = _group_row(conn, account)
        if group is not None and req.relation is not None and req.relation.strip():
            conn.execute(
                "UPDATE care_members SET relation = ? WHERE group_id = ? AND account = ?",
                (req.relation.strip(), group["id"], account),
            )
        if req.device_type is not None and req.device_type.strip():
            conn.execute(
                """
                INSERT INTO presence (account, device_type, updated_at)
                VALUES (?, ?, 0)
                ON CONFLICT(account) DO UPDATE SET device_type = excluded.device_type
                """,
                (account, req.device_type.strip().upper()),
            )
        if req.avatar_base64 is not None:
            conn.execute(
                "UPDATE users SET avatar_base64 = ? WHERE account = ?",
                (req.avatar_base64, account),
            )
        conn.commit()
        return {"ok": True, "updated_at": now}
    finally:
        conn.close()
````

### `server/backend/app/routers/checkins.py`

> 打卡与打卡任务。

````python
"""双人打卡接口。"""

import sqlite3
import time
from typing import Optional

from fastapi import APIRouter, Header

from ..db import _connect
from ..helpers import _group_row, _nickname_of, _parse_date
from ..schemas import CheckInRequest
from ..security import _require_user

router = APIRouter()

@router.post("/api/care/checkins/toggle")
def toggle_check_in(req: CheckInRequest, authorization: Optional[str] = Header(default=None)):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        account = user["account"]
        day = _parse_date(req.date)
        now = int(time.time())
        if req.checked:
            conn.execute(
                """
                INSERT INTO check_ins (date, account, note, goal, image_base64, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(date, account) DO UPDATE SET
                    note = excluded.note,
                    goal = excluded.goal,
                    image_base64 = excluded.image_base64,
                    updated_at = excluded.updated_at
                """,
                (
                    day,
                    account,
                    req.note.strip(),
                    req.goal.strip(),
                    req.image_base64,
                    now,
                ),
            )
        else:
            conn.execute(
                "DELETE FROM check_ins WHERE date = ? AND account = ?", (day, account)
            )
        conn.commit()
        return _checkin_day_payload(conn, account, day)
    finally:
        conn.close()


@router.get("/api/care/checkins")
def list_check_ins(
    start: str,
    end: str,
    authorization: Optional[str] = Header(default=None),
):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        start_day = _parse_date(start)
        end_day = _parse_date(end)
        group = _group_row(conn, user["account"])
        if group is None:
            return {"records": []}
        accounts = [
            row["account"]
            for row in conn.execute(
                "SELECT account FROM care_members WHERE group_id = ?", (group["id"],)
            ).fetchall()
        ]
        placeholders = ",".join("?" for _ in accounts)
        rows = conn.execute(
            f"""
            SELECT c.date, c.account, c.note, c.goal, c.image_base64, c.updated_at, u.nickname
            FROM check_ins c
            LEFT JOIN users u ON u.account = c.account
            WHERE c.date BETWEEN ? AND ? AND c.account IN ({placeholders})
            ORDER BY c.date ASC
            """,
            (start_day, end_day, *accounts),
        ).fetchall()
        return {
            "records": [
                {
                    "date": row["date"],
                    "account": row["account"],
                    "nickname": row["nickname"] or _nickname_of(row["account"]),
                    "note": row["note"],
                    "goal": row["goal"],
                    "image_base64": row["image_base64"],
                    "updated_at": row["updated_at"],
                    "is_self": row["account"] == user["account"],
                }
                for row in rows
            ]
        }
    finally:
        conn.close()


def _checkin_day_payload(conn: sqlite3.Connection, viewer: str, day: str) -> dict:
    group = _group_row(conn, viewer)
    if group is None:
        return {"date": day, "records": []}
    accounts = [
        row["account"]
        for row in conn.execute(
            "SELECT account FROM care_members WHERE group_id = ?", (group["id"],)
        ).fetchall()
    ]
    placeholders = ",".join("?" for _ in accounts)
    rows = conn.execute(
        f"""
        SELECT c.date, c.account, c.note, c.goal, c.image_base64, c.updated_at, u.nickname
        FROM check_ins c
        LEFT JOIN users u ON u.account = c.account
        WHERE c.date = ? AND c.account IN ({placeholders})
        """,
        (day, *accounts),
    ).fetchall()
    return {
        "date": day,
        "records": [
            {
                "date": row["date"],
                "account": row["account"],
                "nickname": row["nickname"] or _nickname_of(row["account"]),
                "note": row["note"],
                "goal": row["goal"],
                "image_base64": row["image_base64"],
                "updated_at": row["updated_at"],
                "is_self": row["account"] == viewer,
            }
            for row in rows
        ],
    }
````

### `server/backend/app/routers/devices.py`

> 设备加入、上报、设备码绑定与解绑。

````python
"""ESP32 设备成员接口。"""

import hmac as hmac_mod
import re
import secrets
import time
from typing import Optional

from fastapi import APIRouter, Header, HTTPException

from ..config import DEVICE_JOIN_SECRET, MAX_GROUP_DEVICES
from ..db import _connect
from ..helpers import _device_account, _device_member_payload, _group_row
from ..schemas import (
    DeviceCodeBindRequest,
    DeviceJoinRequest,
    DevicePresenceRequest,
)
from ..security import _decode_device_code, _require_user

router = APIRouter()

@router.post("/api/care/devices/join")
def join_device(
    req: DeviceJoinRequest,
    authorization: Optional[str] = Header(default=None),
):
    """把 ESP32 加入关心组。

    - App 已登录：用用户 Token 授权，可带当前关心组的邀请码做双重校验；
    - ESP32 自己：没有用户 Token，用 device_secret + 邀请码换取 device_token。
    """
    device_id = req.device_id.strip()
    if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,64}", device_id):
        raise HTTPException(
            status_code=400,
            detail="设备 ID 只能包含字母、数字、下划线、点、冒号或短横线（1-64 位）",
        )
    code = req.invite_code.strip().upper()
    conn = _connect()
    try:
        device_self = not authorization
        if authorization:
            user = _require_user(conn, authorization)
            own = _group_row(conn, user["account"])
            if own is None:
                raise HTTPException(
                    status_code=409, detail="请先创建或加入关心组，再把设备加进来"
                )
            if code and own["invite_code"] != code:
                raise HTTPException(
                    status_code=403, detail="邀请码不是你当前所在的关心组"
                )
            group_id = own["id"]
            invite_code = own["invite_code"]
            added_by = user["account"]
        else:
            if not code:
                raise HTTPException(status_code=400, detail="请输入邀请码")
            if not hmac_mod.compare_digest(
                req.device_secret.strip(), DEVICE_JOIN_SECRET
            ):
                raise HTTPException(status_code=403, detail="设备密钥不正确")
            group = conn.execute(
                "SELECT * FROM care_groups WHERE invite_code = ?", (code,)
            ).fetchone()
            if group is None:
                raise HTTPException(status_code=404, detail="邀请码不存在")
            group_id = group["id"]
            invite_code = group["invite_code"]
            added_by = "esp32"

        existing = conn.execute(
            "SELECT * FROM group_devices WHERE device_id = ?", (device_id,)
        ).fetchone()
        if existing is not None:
            if existing["group_id"] != group_id:
                raise HTTPException(
                    status_code=409, detail="该设备已加入其他关心组，请先移除"
                )
            if req.device_name.strip() or req.relation.strip():
                conn.execute(
                    "UPDATE group_devices SET name = ?, relation = ? "
                    "WHERE group_id = ? AND device_id = ?",
                    (
                        req.device_name.strip() or existing["name"],
                        req.relation.strip() or existing["relation"],
                        group_id,
                        device_id,
                    ),
                )
            # 设备先被 App 加进组、之后自己来换取 Token：补发一个。
            if device_self and not existing["token"]:
                conn.execute(
                    "UPDATE group_devices SET token = ? "
                    "WHERE group_id = ? AND device_id = ?",
                    (secrets.token_hex(24), group_id, device_id),
                )
        else:
            count = conn.execute(
                "SELECT COUNT(*) AS c FROM group_devices WHERE group_id = ?",
                (group_id,),
            ).fetchone()["c"]
            if count >= MAX_GROUP_DEVICES:
                raise HTTPException(
                    status_code=409,
                    detail=f"该关心组最多添加 {MAX_GROUP_DEVICES} 台设备",
                )
            now = int(time.time())
            conn.execute(
                "INSERT INTO group_devices "
                "(group_id, device_id, name, relation, added_by, added_at, token) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    group_id,
                    device_id,
                    req.device_name.strip() or device_id,
                    req.relation.strip() or "设备",
                    added_by,
                    now,
                    secrets.token_hex(24) if device_self else "",
                ),
            )
        conn.execute(
            "INSERT INTO presence (account, device_type, updated_at) VALUES (?, 'ESP32', 0) "
            "ON CONFLICT(account) DO UPDATE SET device_type = 'ESP32'",
            (_device_account(device_id),),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM group_devices WHERE group_id = ? AND device_id = ?",
            (group_id, device_id),
        ).fetchone()
        member = _device_member_payload(conn, row)
        return {
            "ok": True,
            "group_id": group_id,
            "invite_code": invite_code,
            "device": member,
            "device_token": row["token"] if device_self else "",
        }
    finally:
        conn.close()


@router.post("/api/care/devices/{device_id}/presence")
def update_device_presence(
    device_id: str,
    req: DevicePresenceRequest,
    authorization: Optional[str] = Header(default=None),
    x_device_token: Optional[str] = Header(default=None),
):
    """上报设备状态：App（用户 Token）或 ESP32（X-Device-Token）都可以。"""
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM group_devices WHERE device_id = ?", (device_id.strip(),)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="该设备还没有加入关心组")

        allowed = False
        if authorization:
            user = _require_user(conn, authorization)
            own = _group_row(conn, user["account"])
            allowed = own is not None and own["id"] == row["group_id"]
        elif x_device_token:
            allowed = bool(row["token"]) and hmac_mod.compare_digest(
                x_device_token, row["token"]
            )
        if not allowed:
            raise HTTPException(status_code=403, detail="没有权限上报该设备状态")

        now = int(time.time())
        account = _device_account(row["device_id"])
        conn.execute(
            """
            INSERT INTO presence (
                account, lat, lon, status, activity_note, battery,
                device_type, mood_emoji, mood_message, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 'ESP32', '🙂', ?, ?)
            ON CONFLICT(account) DO UPDATE SET
                lat = excluded.lat,
                lon = excluded.lon,
                status = excluded.status,
                activity_note = excluded.activity_note,
                battery = excluded.battery,
                device_type = 'ESP32',
                mood_message = excluded.mood_message,
                updated_at = excluded.updated_at
            """,
            (
                account,
                req.lat,
                req.lon,
                req.status.upper(),
                req.activity_note,
                max(-1, min(100, req.battery)),
                req.mood_message,
                now,
            ),
        )
        conn.commit()
        return {"ok": True, "device_id": row["device_id"], "updated_at": now}
    finally:
        conn.close()


@router.post("/api/care/devices/bind-code")
def bind_device_code(
    req: DeviceCodeBindRequest,
    authorization: Optional[str] = Header(default=None),
):
    """手机输入设备码绑定设备：设备码解密出 deviceId，直接加入当前关心组。"""
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        group = _group_row(conn, user["account"])
        if group is None:
            raise HTTPException(status_code=409, detail="请先创建或加入关心组")
        device_id = _decode_device_code(req.code)
        existing = conn.execute(
            "SELECT * FROM group_devices WHERE device_id = ?", (device_id,)
        ).fetchone()
        if existing is not None and existing["group_id"] != group["id"]:
            raise HTTPException(status_code=409, detail="该设备已绑定到另一个关心组")
        name = (req.name or "").strip() or device_id
        now = int(time.time())
        token = secrets.token_hex(16)
        if existing is None:
            conn.execute(
                """
                INSERT INTO group_devices
                    (group_id, device_id, name, relation, added_by, added_at, token)
                VALUES (?, ?, ?, '设备', ?, ?, ?)
                """,
                (group["id"], device_id, name, user["account"], now, token),
            )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM group_devices WHERE group_id = ? AND device_id = ?",
            (group["id"], device_id),
        ).fetchone()
        return {
            "ok": True,
            "group_id": group["id"],
            "device": _device_member_payload(conn, row),
        }
    finally:
        conn.close()


@router.delete("/api/care/devices/{device_id}")
def remove_device(
    device_id: str,
    authorization: Optional[str] = Header(default=None),
):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        own = _group_row(conn, user["account"])
        if own is None:
            raise HTTPException(status_code=409, detail="你还没有加入关心组")
        row = conn.execute(
            "SELECT * FROM group_devices WHERE device_id = ?", (device_id.strip(),)
        ).fetchone()
        if row is None or row["group_id"] != own["id"]:
            raise HTTPException(status_code=404, detail="关心组里没有这台设备")
        conn.execute(
            "DELETE FROM group_devices WHERE group_id = ? AND device_id = ?",
            (own["id"], row["device_id"]),
        )
        conn.execute(
            "DELETE FROM presence WHERE account = ?",
            (_device_account(row["device_id"]),),
        )
        conn.commit()
        return {"ok": True, "device_id": row["device_id"]}
    finally:
        conn.close()
````

### `server/backend/app/routers/groups.py`

> 关心组创建、加入、审批、移除、解散与退出。

````python
"""关心组创建、加入、审批与成员管理接口。"""

import time
from typing import Optional

from fastapi import APIRouter, Header, HTTPException

from ..config import MAX_GROUP_MEMBERS
from ..db import _connect
from ..helpers import (
    _device_account,
    _group_count,
    _group_payload,
    _group_row,
    _new_invite_code,
    _set_active_group,
)
from ..schemas import GroupCreateRequest, GroupJoinRequest
from ..security import (
    _encrypt_group_password,
    _require_user,
    _verify_group_password,
)

router = APIRouter()

@router.get("/api/care/group")
def get_group(authorization: Optional[str] = Header(default=None)):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        return _group_payload(conn, user["account"])
    finally:
        conn.close()


@router.post("/api/care/group/create")
def create_group(
    req: Optional[GroupCreateRequest] = None,
    authorization: Optional[str] = Header(default=None),
):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        account = user["account"]
        password = (req.password if req else "").strip()
        if len(password) < 4:
            raise HTTPException(status_code=400, detail="请设置至少 4 位的关心组验证密码")
        name = (req.name if req else "").strip() or "关心组"
        now = int(time.time())
        code = _new_invite_code(conn)
        cursor = conn.execute(
            "INSERT INTO care_groups (invite_code, name, join_password, created_by, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (code, name[:24], _encrypt_group_password(password), account, now),
        )
        group_id = cursor.lastrowid
        conn.execute(
            "INSERT INTO care_members (group_id, account, relation, role, joined_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (group_id, account, "我", "owner", now),
        )
        _set_active_group(conn, account, group_id)
        conn.commit()
        return _group_payload(
            conn, account, _group_row(conn, account, group_id)
        )
    finally:
        conn.close()


@router.post("/api/care/group/join")
def join_group(req: GroupJoinRequest, authorization: Optional[str] = Header(default=None)):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        account = user["account"]
        code = req.invite_code.strip().upper()
        if not code:
            raise HTTPException(status_code=400, detail="请输入邀请码")

        group = conn.execute(
            "SELECT * FROM care_groups WHERE invite_code = ?", (code,)
        ).fetchone()
        if group is None:
            raise HTTPException(status_code=404, detail="邀请码不存在")

        member = conn.execute(
            "SELECT 1 FROM care_members WHERE group_id = ? AND account = ?",
            (group["id"], account),
        ).fetchone()
        if member is not None:
            _set_active_group(conn, account, group["id"])
            conn.commit()
            return _group_payload(conn, account, _group_row(conn, account, group["id"]))

        if _group_count(conn, group["id"]) >= MAX_GROUP_MEMBERS:
            raise HTTPException(status_code=409, detail="该关心组已满")
        if group["join_password"] and not _verify_group_password(
            group["join_password"], req.password.strip()
        ):
            raise HTTPException(status_code=403, detail="关心组验证密码不正确")

        now = int(time.time())
        if group["join_password"]:
            # 需要组长审批：先写 pending，组长通过后才真正成为成员。
            conn.execute(
                """
                INSERT INTO join_requests (group_id, account, relation, status, created_at)
                VALUES (?, ?, ?, 'pending', ?)
                ON CONFLICT(group_id, account) DO UPDATE SET
                    relation = excluded.relation,
                    status = 'pending',
                    created_at = excluded.created_at,
                    reviewed_at = 0,
                    reviewed_by = ''
                """,
                (group["id"], account, req.relation.strip() or "家人", now),
            )
            conn.commit()
            return {
                "in_group": False,
                "pending": True,
                "message": "已提交加入申请，等待组长确认",
                "group": {
                    "id": group["id"],
                    "invite_code": group["invite_code"],
                    "name": group["name"] or "关心组",
                    "created_by": group["created_by"],
                    "created_at": group["created_at"],
                    "role": "",
                    "has_password": True,
                    "member_count": _group_count(conn, group["id"]),
                    "device_count": 0,
                    "pending_count": 0,
                },
                "me": None,
                "members": [],
                "devices": [],
                "partner": None,
                "requests": [],
            }
        # 兼容旧组（未设置密码）：直接加入。
        conn.execute(
            "INSERT INTO care_members (group_id, account, relation, role, joined_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (group["id"], account, req.relation.strip() or "家人", "member", now),
        )
        _set_active_group(conn, account, group["id"])
        conn.commit()
        return _group_payload(conn, account, _group_row(conn, account, group["id"]))
    finally:
        conn.close()


@router.get("/api/care/groups")
def list_groups(authorization: Optional[str] = Header(default=None)):
    """一个账号加入的全部关心组，用于首页/亲友页的左右滑动卡片。"""
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        account = user["account"]
        rows = conn.execute(
            "SELECT group_id FROM care_members WHERE account = ? ORDER BY joined_at DESC",
            (account,),
        ).fetchall()
        groups = []
        for row in rows:
            group = _group_row(conn, account, row["group_id"])
            if group is not None:
                groups.append(_group_payload(conn, account, group))
        return {"groups": groups}
    finally:
        conn.close()


@router.post("/api/care/groups/{group_id}/activate")
def activate_group(group_id: int, authorization: Optional[str] = Header(default=None)):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        account = user["account"]
        group = _group_row(conn, account, group_id)
        if group is None:
            raise HTTPException(status_code=404, detail="你不在这个关心组中")
        _set_active_group(conn, account, group_id)
        conn.commit()
        return _group_payload(conn, account, group)
    finally:
        conn.close()


@router.post("/api/care/group/requests/{request_id}/approve")
def approve_join_request(
    request_id: int, authorization: Optional[str] = Header(default=None)
):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        account = user["account"]
        request = conn.execute(
            "SELECT * FROM join_requests WHERE id = ?", (request_id,)
        ).fetchone()
        if request is None or request["status"] != "pending":
            raise HTTPException(status_code=404, detail="申请不存在或已处理")
        owner = conn.execute(
            "SELECT role FROM care_members WHERE group_id = ? AND account = ?",
            (request["group_id"], account),
        ).fetchone()
        if owner is None or owner["role"] != "owner":
            raise HTTPException(status_code=403, detail="只有组长可以审批加入申请")
        if _group_count(conn, request["group_id"]) >= MAX_GROUP_MEMBERS:
            raise HTTPException(status_code=409, detail="该关心组已满")
        now = int(time.time())
        conn.execute(
            "INSERT OR IGNORE INTO care_members (group_id, account, relation, role, joined_at) "
            "VALUES (?, ?, ?, 'member', ?)",
            (request["group_id"], request["account"], request["relation"], now),
        )
        conn.execute(
            "UPDATE join_requests SET status = 'approved', reviewed_at = ?, reviewed_by = ? "
            "WHERE id = ?",
            (now, account, request_id),
        )
        _set_active_group(conn, request["account"], request["group_id"])
        conn.commit()
        return _group_payload(conn, account)
    finally:
        conn.close()


@router.post("/api/care/group/requests/{request_id}/reject")
def reject_join_request(
    request_id: int, authorization: Optional[str] = Header(default=None)
):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        account = user["account"]
        request = conn.execute(
            "SELECT * FROM join_requests WHERE id = ?", (request_id,)
        ).fetchone()
        if request is None or request["status"] != "pending":
            raise HTTPException(status_code=404, detail="申请不存在或已处理")
        owner = conn.execute(
            "SELECT role FROM care_members WHERE group_id = ? AND account = ?",
            (request["group_id"], account),
        ).fetchone()
        if owner is None or owner["role"] != "owner":
            raise HTTPException(status_code=403, detail="只有组长可以处理加入申请")
        conn.execute(
            "UPDATE join_requests SET status = 'rejected', reviewed_at = ?, reviewed_by = ? "
            "WHERE id = ?",
            (int(time.time()), account, request_id),
        )
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()


@router.delete("/api/care/group/members/{member_account}")
def remove_group_member(
    member_account: str, authorization: Optional[str] = Header(default=None)
):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        account = user["account"]
        if member_account == account:
            raise HTTPException(status_code=400, detail="不能移除自己，请使用退出关心组")
        group = _group_row(conn, account)
        if group is None or group["role"] != "owner":
            raise HTTPException(status_code=403, detail="只有组长可以移除组员")
        target = conn.execute(
            "SELECT 1 FROM care_members WHERE group_id = ? AND account = ?",
            (group["id"], member_account),
        ).fetchone()
        if target is None:
            raise HTTPException(status_code=404, detail="该成员不在当前关心组")
        conn.execute(
            "DELETE FROM care_members WHERE group_id = ? AND account = ?",
            (group["id"], member_account),
        )
        next_group = conn.execute(
            "SELECT group_id FROM care_members WHERE account = ? ORDER BY joined_at DESC LIMIT 1",
            (member_account,),
        ).fetchone()
        _set_active_group(
            conn, member_account, int(next_group["group_id"]) if next_group else 0
        )
        conn.commit()
        return _group_payload(conn, account)
    finally:
        conn.close()


@router.delete("/api/care/groups/{group_id}")
def dissolve_group(group_id: int, authorization: Optional[str] = Header(default=None)):
    """组长解散关心组：清空组内数据，所有成员回到无组状态。"""
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        account = user["account"]
        group = _group_row(conn, account, group_id)
        if group is None:
            raise HTTPException(status_code=404, detail="你不在这个关心组中")
        if group["role"] != "owner":
            raise HTTPException(status_code=403, detail="只有组长可以解散关心组")
        members = conn.execute(
            "SELECT account FROM care_members WHERE group_id = ?", (group_id,)
        ).fetchall()
        for member in members:
            _set_active_group(conn, member["account"], 0)
        for device in conn.execute(
            "SELECT device_id FROM group_devices WHERE group_id = ?", (group_id,)
        ).fetchall():
            conn.execute(
                "DELETE FROM presence WHERE account = ?",
                (_device_account(device["device_id"]),),
            )
        for table in (
            "group_devices",
            "care_members",
            "join_requests",
            "reminders",
            "nudges",
            "chat_messages",
            "checkin_tasks",
            "schedule_posts",
        ):
            conn.execute(f"DELETE FROM {table} WHERE group_id = ?", (group_id,))
        conn.execute("DELETE FROM care_groups WHERE id = ?", (group_id,))
        conn.commit()
        return {"ok": True, "dissolved": True}
    finally:
        conn.close()


@router.post("/api/care/group/leave")
def leave_group(authorization: Optional[str] = Header(default=None)):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        account = user["account"]
        group = _group_row(conn, account)
        if group is None:
            return {"ok": True, "in_group": False}
        conn.execute(
            "DELETE FROM care_members WHERE group_id = ? AND account = ?",
            (group["id"], account),
        )
        remaining = conn.execute(
            "SELECT COUNT(*) AS c FROM care_members WHERE group_id = ?", (group["id"],)
        ).fetchone()["c"]
        if remaining == 0:
            for device in conn.execute(
                "SELECT device_id FROM group_devices WHERE group_id = ?",
                (group["id"],),
            ).fetchall():
                conn.execute(
                    "DELETE FROM presence WHERE account = ?",
                    (_device_account(device["device_id"]),),
                )
            conn.execute(
                "DELETE FROM group_devices WHERE group_id = ?", (group["id"],)
            )
            conn.execute("DELETE FROM reminders WHERE group_id = ?", (group["id"],))
            conn.execute("DELETE FROM nudges WHERE group_id = ?", (group["id"],))
            conn.execute("DELETE FROM care_groups WHERE id = ?", (group["id"],))
        next_group = conn.execute(
            "SELECT group_id FROM care_members WHERE account = ? ORDER BY joined_at DESC LIMIT 1",
            (account,),
        ).fetchone()
        _set_active_group(conn, account, int(next_group["group_id"]) if next_group else 0)
        conn.commit()
        return {"ok": True, "in_group": False}
    finally:
        conn.close()
````

### `server/backend/app/routers/health.py`

````python
"""健康检查接口。"""

from fastapi import APIRouter

from ..config import APP_VERSION

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "service": "care-backend", "version": APP_VERSION}
````

### `server/backend/app/routers/llm.py`

> `/v1/chat/completions`：转发 Ollama 并带规则回退。

````python
"""OpenAI 兼容的大模型代理接口。"""

import httpx
from fastapi import APIRouter

from ..config import LLM_UPSTREAM_API_KEY, LLM_UPSTREAM_URL
from ..schemas import ChatRequest

router = APIRouter()

def _user_content(req: ChatRequest) -> str:
    for message in reversed(req.messages):
        if message.role == "user" and message.content:
            return message.content
    return ""


def _rule_based(content: str) -> str:
    """上游大模型不可用时的多角度兜底建议。

    返回带 [角度] 标签的多行文本，客户端会解析成 action / words / surprise / love；
    即使没有配置大模型，关心建议也不会退化成干巴巴的一句话。
    """
    couple = any(word in content for word in ("情侣", "恋人", "伴侣", "爱人"))
    if "医学异常" in content or "跌倒" in content or "求助" in content:
        tips = [
            ("马上做", "先直接打电话确认 TA 是否清醒、能否应答；联系不上就马上联系 TA 身边的人。"),
            ("说句话", "如果 TA 能回应，只说短句：“我在，别怕，告诉我你现在在哪里。”"),
            ("小惊喜", "把 TA 的位置、紧急联系人和常用药整理好，关键时刻能直接用到。"),
        ]
    elif "重度疲劳" in content:
        tips = [
            ("马上做", "先打电话确认 TA 是否还能安全停车，提醒 TA 靠边休息，别硬撑。"),
            ("说句话", "说“我不催你，先找地方停好，到了告诉我”，让 TA 不用分心解释。"),
            ("小惊喜", "帮 TA 查好最近的服务区或停车场，等 TA 停稳再发过去。"),
        ]
    elif "中度疲劳" in content:
        tips = [
            ("马上做", "给 TA 发一个十五分钟的休息计时，到点提醒 TA 下车走走、喝口水。"),
            ("说句话", "别问“还要多久”，先说“安全第一，晚一点也没关系”。"),
            ("小惊喜", "点一杯热饮送到 TA 的下一站，备注“提神，不用回”。"),
        ]
    elif "轻度疲劳" in content:
        tips = [
            ("马上做", "留意 TA 的位置变化，提醒 TA 找个安全的地方停一停。"),
            ("说句话", "发一句“有点累就歇一下，我等你”，比“注意安全”更具体。"),
            ("小惊喜", "把 TA 爱听的歌单发过去，让回程没那么无聊。"),
        ]
    elif "学习" in content or "自习" in content or "工作" in content or "忙" in content:
        tips = [
            ("马上做", "给 TA 点一杯热饮或一份水果，备注“忙完再喝”，不打扰但被看见。"),
            ("说句话", "发一句“看到你在忙，不催你，忙完告诉我”，把关心留在不打扰的位置。"),
            ("小惊喜", "把 TA 最近提到想看的电影记下来，等忙完那天直接买好票。"),
        ]
    elif "开车" in content or "驾驶" in content or "路上" in content:
        tips = [
            ("马上做", "等 TA 到达后再联系；现在只发一条“到了说一声”，不要连续追问。"),
            ("说句话", "把“注意安全”换成“我在终点等你”，具体的目的地比空泛的叮嘱更安心。"),
            ("小惊喜", "提前查好目的地附近的停车位和天气，等 TA 停稳再发过去。"),
        ]
    elif "睡" in content or "晚安" in content:
        tips = [
            ("马上做", "把想说的话写成一句晚安留言，明早 TA 醒来第一眼就能看到。"),
            ("说句话", "别叫醒 TA，留一句“晚安，明天见”，让关心停在门口。"),
            ("小惊喜", "帮 TA 把明天的天气和穿衣建议准备好，早上再发过去。"),
        ]
    elif "雨" in content or "降温" in content or "天气" in content:
        tips = [
            ("马上做", "查一下 TA 所在城市未来几小时的降雨，提醒 TA 带伞或改走有遮挡的路线。"),
            ("说句话", "把“注意身体”换成“你那边降温了，外套穿厚一点”，具体才像真的关心。"),
            ("小惊喜", "给 TA 寄一件薄外套或一双暖袜，让天气提醒变成能摸到的东西。"),
        ]
    else:
        tips = [
            ("马上做", "翻一下你们的聊天记录，找一件 TA 提过的小事，今天替 TA 做掉。"),
            ("说句话", "发一张此刻的照片，配一句“看到这个就想到你”，比“在干嘛”更有画面。"),
            ("小惊喜", "在 TA 常用的 App 里留一条只有你们懂的暗号，等 TA 自己发现。"),
        ]
    if couple and "医学异常" not in content and "跌倒" not in content:
        tips.append(("情话", "今天也没有特别的事，只是又比昨天多喜欢你一点。"))
    return "\n".join(f"{index}. [{label}] {text}" for index, (label, text) in enumerate(tips, 1))


def _openai_response(content: str) -> dict:
    return {"choices": [{"message": {"role": "assistant", "content": content}}]}


async def _proxy_upstream(req: ChatRequest) -> dict:
    headers = {}
    if LLM_UPSTREAM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_UPSTREAM_API_KEY}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(LLM_UPSTREAM_URL, json=req.model_dump(), headers=headers)
        response.raise_for_status()
        return response.json()


@router.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    if LLM_UPSTREAM_URL:
        try:
            return await _proxy_upstream(req)
        except Exception:
            pass  # 上游不可用时回退到规则化建议
    return _openai_response(_rule_based(_user_content(req)))
````

### `server/backend/app/routers/messages.py`

> 留言收发。

````python
"""留言墙接口。"""

import sqlite3
import time
from typing import Optional

from fastapi import APIRouter, Header, HTTPException

from ..db import _connect
from ..helpers import _group_row, _nickname_of
from ..schemas import ChatMessageRequest
from ..security import _require_user

router = APIRouter()

def _chat_payload(row: sqlite3.Row, viewer: str) -> dict:
    return {
        "id": row["id"],
        "message": row["message"],
        "from_account": row["from_account"],
        "from_nickname": row["nickname"] or _nickname_of(row["from_account"]),
        "is_mine": row["from_account"] == viewer,
        "created_at": row["created_at"],
    }


@router.post("/api/care/messages")
def send_chat_message(
    req: ChatMessageRequest,
    authorization: Optional[str] = Header(default=None),
):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        group = _group_row(conn, user["account"])
        if group is None:
            raise HTTPException(status_code=409, detail="请先绑定亲友")
        message = req.message.strip()
        if not message:
            raise HTTPException(status_code=400, detail="留言不能为空")
        now = int(time.time())
        cursor = conn.execute(
            "INSERT INTO chat_messages (group_id, from_account, message, created_at) VALUES (?, ?, ?, ?)",
            (group["id"], user["account"], message[:2000], now),
        )
        conn.commit()
        row = conn.execute(
            "SELECT m.*, u.nickname FROM chat_messages m LEFT JOIN users u ON u.account = m.from_account WHERE m.id = ?",
            (cursor.lastrowid,),
        ).fetchone()
        return {"message": _chat_payload(row, user["account"])}
    finally:
        conn.close()


@router.get("/api/care/messages")
def list_chat_messages(
    since_id: int = 0,
    limit: int = 100,
    authorization: Optional[str] = Header(default=None),
):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        group = _group_row(conn, user["account"])
        if group is None:
            return {"messages": []}
        rows = conn.execute(
            """
            SELECT m.*, u.nickname
            FROM chat_messages m
            LEFT JOIN users u ON u.account = m.from_account
            WHERE m.group_id = ? AND m.id > ?
            ORDER BY m.id ASC LIMIT ?
            """,
            (group["id"], max(0, since_id), max(1, min(200, limit))),
        ).fetchall()
        return {"messages": [_chat_payload(row, user["account"]) for row in rows]}
    finally:
        conn.close()
````

### `server/backend/app/routers/nudge.py`

> 轻推发送与拉取。

````python
"""关心消息接口。"""

import time
from typing import Optional

from fastapi import APIRouter, Header, HTTPException

from ..db import _connect
from ..helpers import _group_row, _nickname_of
from ..schemas import NudgeRequest
from ..security import _require_user

router = APIRouter()

@router.post("/api/care/nudge")
def send_nudge(req: NudgeRequest, authorization: Optional[str] = Header(default=None)):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        account = user["account"]
        group = _group_row(conn, account)
        if group is None:
            raise HTTPException(status_code=409, detail="请先绑定亲友")
        partner = conn.execute(
            "SELECT account FROM care_members WHERE group_id = ? AND account != ?",
            (group["id"], account),
        ).fetchone()
        if partner is None:
            raise HTTPException(status_code=409, detail="对方还没有加入关心组")
        conn.execute(
            "INSERT INTO nudges (group_id, from_account, to_account, message, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                group["id"],
                account,
                partner["account"],
                req.message.strip() or "在想你，记得照顾好自己。",
                int(time.time()),
            ),
        )
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()


@router.get("/api/care/nudges")
def list_nudges(
    since_id: int = 0,
    authorization: Optional[str] = Header(default=None),
):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        rows = conn.execute(
            """
            SELECT n.*, u.nickname AS from_nickname
            FROM nudges n
            LEFT JOIN users u ON u.account = n.from_account
            WHERE n.to_account = ? AND n.id > ?
            ORDER BY n.id ASC
            LIMIT 50
            """,
            (user["account"], max(0, since_id)),
        ).fetchall()
        return {
            "nudges": [
                {
                    "id": row["id"],
                    "from_account": row["from_account"],
                    "from_nickname": row["from_nickname"] or _nickname_of(row["from_account"]),
                    "message": row["message"],
                    "created_at": row["created_at"],
                }
                for row in rows
            ]
        }
    finally:
        conn.close()
````

### `server/backend/app/routers/presence.py`

> 位置与状态上报/查询。

````python
"""双方位置与状态接口。"""

import time
from typing import Optional

from fastapi import APIRouter, Header

from ..db import _connect
from ..helpers import _group_payload
from ..schemas import PresenceRequest
from ..security import _require_user

router = APIRouter()

@router.post("/api/care/presence")
def update_presence(req: PresenceRequest, authorization: Optional[str] = Header(default=None)):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        account = user["account"]
        now = int(time.time())
        conn.execute(
            """
            INSERT INTO presence (
                account, lat, lon, status, activity_note, battery,
                device_type, mood_emoji, mood_message, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(account) DO UPDATE SET
                lat = excluded.lat,
                lon = excluded.lon,
                status = excluded.status,
                activity_note = excluded.activity_note,
                battery = excluded.battery,
                device_type = excluded.device_type,
                mood_emoji = excluded.mood_emoji,
                mood_message = excluded.mood_message,
                updated_at = excluded.updated_at
            """,
            (
                account,
                req.lat,
                req.lon,
                req.status,
                req.activity_note,
                max(-1, min(100, req.battery)),
                req.device_type.upper(),
                req.mood_emoji or "🙂",
                req.mood_message,
                now,
            ),
        )
        conn.commit()
        return {"ok": True, "updated_at": now}
    finally:
        conn.close()


@router.get("/api/care/presence")
def get_presence(authorization: Optional[str] = Header(default=None)):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        payload = _group_payload(conn, user["account"])
        return {
            "in_group": payload["in_group"],
            "me": payload["me"],
            "partner": payload["partner"],
            "members": payload["members"],
            "devices": payload.get("devices", []),
        }
    finally:
        conn.close()
````

### `server/backend/app/routers/reminders.py`

> 共享提醒的增删改查。

````python
"""共享提醒接口。"""

import sqlite3
import time
from typing import Optional

from fastapi import APIRouter, Header, HTTPException

from ..db import _connect
from ..helpers import _group_row, _parse_date
from ..schemas import ReminderCreateRequest, ReminderUpdateRequest
from ..security import _require_user

router = APIRouter()

@router.get("/api/care/reminders")
def list_reminders(
    start: str,
    end: str,
    authorization: Optional[str] = Header(default=None),
):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        start_day = _parse_date(start)
        end_day = _parse_date(end)
        group = _group_row(conn, user["account"])
        if group is None:
            return {"reminders": []}
        rows = conn.execute(
            """
            SELECT * FROM reminders
            WHERE group_id = ? AND date BETWEEN ? AND ?
            ORDER BY date ASC, time_minutes ASC
            """,
            (group["id"], start_day, end_day),
        ).fetchall()
        return {"reminders": [_reminder_payload(row, user["account"]) for row in rows]}
    finally:
        conn.close()


@router.post("/api/care/reminders")
def create_reminder(req: ReminderCreateRequest, authorization: Optional[str] = Header(default=None)):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        group = _group_row(conn, user["account"])
        if group is None:
            raise HTTPException(status_code=409, detail="请先绑定亲友")
        day = _parse_date(req.date)
        if not req.title.strip():
            raise HTTPException(status_code=400, detail="提醒内容不能为空")
        now = int(time.time())
        cursor = conn.execute(
            """
            INSERT INTO reminders
                (group_id, date, time_minutes, title, note, enabled, type, created_by, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?)
            """,
            (
                group["id"],
                day,
                max(0, min(24 * 60 - 1, req.time_minutes)),
                req.title.strip(),
                req.note.strip(),
                (req.type or "schedule").strip().lower(),
                user["account"],
                now,
                now,
            ),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM reminders WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return {"reminder": _reminder_payload(row, user["account"])}
    finally:
        conn.close()


@router.patch("/api/care/reminders/{reminder_id}")
def update_reminder(
    reminder_id: int,
    req: ReminderUpdateRequest,
    authorization: Optional[str] = Header(default=None),
):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        group = _group_row(conn, user["account"])
        if group is None:
            raise HTTPException(status_code=409, detail="请先绑定亲友")
        row = conn.execute(
            "SELECT * FROM reminders WHERE id = ? AND group_id = ?",
            (reminder_id, group["id"]),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="提醒不存在")

        day = _parse_date(req.date) if req.date is not None else row["date"]
        time_minutes = (
            max(0, min(24 * 60 - 1, req.time_minutes))
            if req.time_minutes is not None
            else row["time_minutes"]
        )
        title = req.title.strip() if req.title is not None and req.title.strip() else row["title"]
        note = req.note.strip() if req.note is not None else row["note"]
        enabled = int(req.enabled) if req.enabled is not None else row["enabled"]
        reminder_type = (
            (req.type or "schedule").strip().lower()
            if req.type is not None
            else row["type"]
        )
        conn.execute(
            """
            UPDATE reminders
            SET date = ?, time_minutes = ?, title = ?, note = ?, enabled = ?, type = ?, updated_at = ?
            WHERE id = ?
            """,
            (day, time_minutes, title, note, enabled, reminder_type, int(time.time()), reminder_id),
        )
        conn.commit()
        updated = conn.execute(
            "SELECT * FROM reminders WHERE id = ?", (reminder_id,)
        ).fetchone()
        return {"reminder": _reminder_payload(updated, user["account"])}
    finally:
        conn.close()


@router.delete("/api/care/reminders/{reminder_id}")
def delete_reminder(reminder_id: int, authorization: Optional[str] = Header(default=None)):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        group = _group_row(conn, user["account"])
        if group is None:
            raise HTTPException(status_code=409, detail="请先绑定亲友")
        conn.execute(
            "DELETE FROM reminders WHERE id = ? AND group_id = ?",
            (reminder_id, group["id"]),
        )
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()


def _reminder_payload(row: sqlite3.Row, viewer: str) -> dict:
    return {
        "id": row["id"],
        "date": row["date"],
        "time_minutes": row["time_minutes"],
        "title": row["title"],
        "note": row["note"],
        "enabled": bool(row["enabled"]),
        "type": row["type"],
        "created_by": row["created_by"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "is_mine": row["created_by"] == viewer,
    }
````

### `server/backend/app/routers/schedule.py`

> 日程发布与查询。

````python
"""共享日程 / 今天做了什么接口。"""

import sqlite3
import time
from typing import Optional

from fastapi import APIRouter, Header, HTTPException

from ..db import _connect
from ..helpers import _group_row, _nickname_of, _parse_date
from ..schemas import SchedulePostRequest
from ..security import _require_user

router = APIRouter()

def _schedule_payload(row: sqlite3.Row, viewer: str) -> dict:
    return {
        "id": row["id"],
        "date": row["date"],
        "time_minutes": row["time_minutes"],
        "content": row["content"],
        "image_base64": row["image_base64"],
        "author": row["author"],
        "nickname": row["nickname"] or _nickname_of(row["author"]),
        "created_at": row["created_at"],
        "is_mine": row["author"] == viewer,
    }


@router.get("/api/care/schedule")
def list_schedule(
    start: str,
    end: str,
    authorization: Optional[str] = Header(default=None),
):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        group = _group_row(conn, user["account"])
        if group is None:
            return {"posts": []}
        rows = conn.execute(
            """
            SELECT p.*, u.nickname
            FROM schedule_posts p
            LEFT JOIN users u ON u.account = p.author
            WHERE p.group_id = ? AND p.date BETWEEN ? AND ?
            ORDER BY p.date ASC, p.time_minutes ASC, p.id ASC
            """,
            (group["id"], _parse_date(start), _parse_date(end)),
        ).fetchall()
        return {"posts": [_schedule_payload(row, user["account"]) for row in rows]}
    finally:
        conn.close()


@router.post("/api/care/schedule")
def create_schedule(
    req: SchedulePostRequest,
    authorization: Optional[str] = Header(default=None),
):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        group = _group_row(conn, user["account"])
        if group is None:
            raise HTTPException(status_code=409, detail="请先绑定亲友")
        if not req.content.strip():
            raise HTTPException(status_code=400, detail="内容不能为空")
        now = int(time.time())
        cursor = conn.execute(
            """
            INSERT INTO schedule_posts
                (group_id, author, date, time_minutes, content, image_base64, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                group["id"],
                user["account"],
                _parse_date(req.date),
                max(0, min(24 * 60 - 1, req.time_minutes)),
                req.content.strip(),
                req.image_base64,
                now,
            ),
        )
        conn.commit()
        row = conn.execute(
            """
            SELECT p.*, u.nickname
            FROM schedule_posts p
            LEFT JOIN users u ON u.account = p.author
            WHERE p.id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()
        return {"post": _schedule_payload(row, user["account"])}
    finally:
        conn.close()
````

### `server/backend/app/routers/tasks.py`

````python
"""共同任务打卡接口。"""

import sqlite3
import time
from typing import Optional

from fastapi import APIRouter, Header, HTTPException

from ..db import _connect
from ..helpers import _group_row, _parse_date
from ..schemas import CheckInTaskRequest, CheckInTaskToggleRequest
from ..security import _require_user

router = APIRouter()

def _task_payload(row: sqlite3.Row, viewer: str) -> dict:
    is_creator = row["creator"] == viewer
    return {
        "id": row["id"],
        "date": row["date"],
        "title": row["title"],
        "image_base64": row["image_base64"],
        "self_done": bool(row["done_creator"] if is_creator else row["done_other"]),
        "partner_done": bool(row["done_other"] if is_creator else row["done_creator"]),
        "created_by": "self" if is_creator else "partner",
        "created_at": row["created_at"],
    }


@router.get("/api/care/tasks")
def list_tasks(
    start: str,
    end: str,
    authorization: Optional[str] = Header(default=None),
):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        group = _group_row(conn, user["account"])
        if group is None:
            return {"tasks": []}
        rows = conn.execute(
            """
            SELECT * FROM checkin_tasks
            WHERE group_id = ? AND date BETWEEN ? AND ?
            ORDER BY created_at ASC
            """,
            (group["id"], _parse_date(start), _parse_date(end)),
        ).fetchall()
        return {"tasks": [_task_payload(row, user["account"]) for row in rows]}
    finally:
        conn.close()


@router.post("/api/care/tasks")
def create_task(
    req: CheckInTaskRequest,
    authorization: Optional[str] = Header(default=None),
):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        group = _group_row(conn, user["account"])
        if group is None:
            raise HTTPException(status_code=409, detail="请先绑定亲友")
        if not req.title.strip():
            raise HTTPException(status_code=400, detail="任务不能为空")
        now = int(time.time())
        cursor = conn.execute(
            """
            INSERT INTO checkin_tasks
                (group_id, date, title, image_base64, creator, done_creator, done_other, created_at)
            VALUES (?, ?, ?, ?, ?, 0, 0, ?)
            """,
            (
                group["id"],
                _parse_date(req.date),
                req.title.strip(),
                req.image_base64,
                user["account"],
                now,
            ),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM checkin_tasks WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return {"task": _task_payload(row, user["account"])}
    finally:
        conn.close()


@router.patch("/api/care/tasks/{task_id}")
def toggle_task(
    task_id: int,
    req: CheckInTaskToggleRequest,
    authorization: Optional[str] = Header(default=None),
):
    conn = _connect()
    try:
        user = _require_user(conn, authorization)
        group = _group_row(conn, user["account"])
        if group is None:
            raise HTTPException(status_code=409, detail="请先绑定亲友")
        row = conn.execute(
            "SELECT * FROM checkin_tasks WHERE id = ? AND group_id = ?",
            (task_id, group["id"]),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        column = "done_creator" if row["creator"] == user["account"] else "done_other"
        conn.execute(
            f"UPDATE checkin_tasks SET {column} = ? WHERE id = ?",
            (1 if req.done else 0, task_id),
        )
        conn.commit()
        updated = conn.execute(
            "SELECT * FROM checkin_tasks WHERE id = ?", (task_id,)
        ).fetchone()
        return {"task": _task_payload(updated, user["account"])}
    finally:
        conn.close()
````

### `server/backend/app/schemas.py`

> 全部 Pydantic 请求/响应模型。

````python
"""请求 / 响应模型。"""

from typing import List, Optional

from pydantic import BaseModel

from .config import LLM_MODEL

class AuthRequest(BaseModel):
    account: str
    password: str


class AuthResponse(BaseModel):
    account: str
    nickname: str
    token: str
    avatar_base64: str = ""


class GroupCreateRequest(BaseModel):
    name: str = ""
    password: str = ""


class GroupJoinRequest(BaseModel):
    invite_code: str
    relation: str = "家人"
    password: str = ""


class DeviceJoinRequest(BaseModel):
    device_id: str
    invite_code: str = ""
    device_name: str = ""
    relation: str = "设备"
    device_secret: str = ""


class DeviceCodeBindRequest(BaseModel):
    code: str
    name: str = ""


class DevicePresenceRequest(BaseModel):
    lat: float = 0.0
    lon: float = 0.0
    status: str = "ONLINE"
    activity_note: str = ""
    battery: int = 100
    mood_message: str = ""


class PresenceRequest(BaseModel):
    lat: float = 0.0
    lon: float = 0.0
    status: str = "UNKNOWN"
    activity_note: str = ""
    battery: int = -1
    device_type: str = "PHONE"
    mood_emoji: str = "🙂"
    mood_message: str = ""


class CheckInRequest(BaseModel):
    date: str
    checked: bool
    note: str = ""
    goal: str = ""
    image_base64: str = ""


class SchedulePostRequest(BaseModel):
    date: str
    time_minutes: int = 0
    content: str
    image_base64: str = ""


class ChatMessageRequest(BaseModel):
    message: str = ""


class CheckInTaskRequest(BaseModel):
    date: str
    title: str
    image_base64: str = ""


class CheckInTaskToggleRequest(BaseModel):
    done: bool = True


class ReminderCreateRequest(BaseModel):
    date: str
    time_minutes: int
    title: str
    note: str = ""
    type: str = "schedule"


class ReminderUpdateRequest(BaseModel):
    date: Optional[str] = None
    time_minutes: Optional[int] = None
    title: Optional[str] = None
    note: Optional[str] = None
    enabled: Optional[bool] = None
    type: Optional[str] = None


class NudgeRequest(BaseModel):
    message: str = ""


class ProfileRequest(BaseModel):
    nickname: Optional[str] = None
    relation: Optional[str] = None
    device_type: Optional[str] = None
    avatar_base64: Optional[str] = None


class ChatMessage(BaseModel):
    role: str
    content: str = ""


class ChatRequest(BaseModel):
    model: str = LLM_MODEL
    messages: List[ChatMessage] = []
````

### `server/backend/app/security.py`

> PBKDF2 密码、Bearer Token、Fernet 组密码与设备码解码。

````python
"""鉴权、设备码与关心组验证密码的安全工具。"""

import base64
import binascii
import hashlib
import hmac as hmac_mod
import secrets
import sqlite3
import zlib
from typing import Optional

from cryptography.exceptions import InvalidTag
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import HTTPException

from .config import DEVICE_CODE_KEY, GROUP_AES_SECRET

_GROUP_FERNET = Fernet(
    base64.urlsafe_b64encode(hashlib.sha256(GROUP_AES_SECRET.encode("utf-8")).digest())
)


def _encrypt_group_password(password: str) -> str:
    return _GROUP_FERNET.encrypt(password.encode("utf-8")).decode("ascii")


def _verify_group_password(token: str, password: str) -> bool:
    if not token:
        return False
    try:
        return hmac_mod.compare_digest(
            _GROUP_FERNET.decrypt(token.encode("ascii")).decode("utf-8"),
            password,
        )
    except (InvalidToken, ValueError):
        return False


def _decode_device_code(code: str) -> str:
    """解码设备码：TM1|deviceId|crc32，AES-GCM 认证。"""
    try:
        raw = code.strip().replace(" ", "")
        raw += "=" * (-len(raw) % 4)
        packed = base64.urlsafe_b64decode(raw.encode("ascii"))
        if len(packed) <= 12:
            raise ValueError("too short")
        key = hashlib.sha256(DEVICE_CODE_KEY.encode("utf-8")).digest()
        payload = AESGCM(key).decrypt(packed[:12], packed[12:], None).decode("utf-8")
        version, device_id, checksum = payload.split("|")
        if version != "TM1" or not device_id:
            raise ValueError("bad version")
        if f"{zlib.crc32(device_id.encode('utf-8')) & 0xffffffff:08x}" != checksum:
            raise ValueError("bad checksum")
        return device_id
    except (ValueError, binascii.Error, UnicodeDecodeError, InvalidTag) as exc:
        raise HTTPException(status_code=400, detail="设备码无效或已被篡改") from exc


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), 100_000
    ).hex()
    return f"{salt}:{digest}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split(":", 1)
        calc = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt), 100_000
        ).hex()
        return hmac_mod.compare_digest(calc, digest)
    except Exception:
        return False


def _bearer_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少登录凭证")
    value = authorization.strip()
    if value.lower().startswith("bearer "):
        value = value[7:].strip()
    if not value:
        raise HTTPException(status_code=401, detail="缺少登录凭证")
    return value


def _require_user(conn: sqlite3.Connection, authorization: Optional[str]) -> sqlite3.Row:
    token = _bearer_token(authorization)
    row = conn.execute(
        "SELECT account, nickname FROM users WHERE token = ?", (token,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="登录已失效，请重新登录")
    return row
````

<a id="s08-2"></a>

## 步骤 08.2 · 容器与部署脚本

Dockerfile 以 uvicorn 启动 `app.main:app`；compose 同时编排 EMQX、backend 与 Ollama。

本步骤涉及的文件：

- `server/backend/Dockerfile`
- `server/backend/requirements.txt`
- `server/docker-compose.yml`
- `server/deploy.sh`

### `server/backend/Dockerfile`

````dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN mkdir -p /data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
````

### `server/backend/requirements.txt`

````text
fastapi>=0.110
uvicorn>=0.29
httpx>=0.27
cryptography>=42
````

### `server/docker-compose.yml`

````yaml
services:
  emqx:
    image: emqx/emqx:5.8.0
    container_name: care-emqx
    restart: unless-stopped
    ports:
      - "1883:1883"    # MQTT（App / ESP32）
      - "8083:8083"    # MQTT over WebSocket
      - "18083:18083"  # EMQX Dashboard，默认 admin/public，部署后请立即修改
    volumes:
      - emqx_data:/opt/emqx/data
      - emqx_log:/opt/emqx/log

  ollama:
    image: ollama/ollama:latest
    container_name: care-ollama
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

  backend:
    build: ./backend
    container_name: care-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      DB_PATH: /data/care.db
      # 服务器本地模型：Ollama 的 OpenAI 兼容接口，不调用 DeepSeek 等外部 API
      LLM_UPSTREAM_URL: http://ollama:11434/v1/chat/completions
      LLM_MODEL: qwen2.5:3b
    volumes:
      - backend_data:/data

volumes:
  emqx_data:
  emqx_log:
  backend_data:
  ollama_data:
````

### `server/deploy.sh`

````bash
#!/usr/bin/env bash
# 念安后端一键部署（在阿里云服务器上执行）
# 用法：cd server && bash deploy.sh
set -euo pipefail

cd "$(dirname "$0")"

echo "==> 检查 Docker"
if ! command -v docker >/dev/null 2>&1; then
  echo "未找到 docker，请先在服务器安装 Docker 与 docker compose 插件。"
  exit 1
fi

echo "==> 构建并启动 EMQX + 念安后端"
docker compose up -d --build

echo "==> 等待后端启动"
for i in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo "==> 健康检查"
curl -fsS http://127.0.0.1:8000/health || {
  echo "后端健康检查失败，请执行：docker compose logs -f backend"
  exit 1
}
echo
echo "==> 运行状态"
docker compose ps
echo
echo "部署完成："
echo "  API:      http://<服务器公网IP>:8000"
echo "  文档:     http://<服务器公网IP>:8000/docs"
echo "  MQTT:     tcp://<服务器公网IP>:1883"
echo "  EMQX:     http://<服务器公网IP>:18083（默认 admin/public，请立即修改）"
echo
echo "注意：阿里云安全组需要放行 TCP 8000 / 1883 / 18083。"
````

<a id="s08-3"></a>

## 步骤 08.3 · 后端接口测试

用 FastAPI TestClient 覆盖关心组、设备绑定与成员管理流程。

本步骤涉及的文件：

- `server/tests/setup_demo_accounts.py`
- `server/tests/test_care_api.py`
- `server/tests/test_device_members.py`

### `server/tests/setup_demo_accounts.py`

````python
import json
import sys
from datetime import date, timedelta

import httpx

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8010"
client = httpx.Client(base_url=BASE, timeout=10, headers={"X-App-Version": "5.0.1"})


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def register_or_login(account, password="123456"):
    response = client.post("/api/auth/register", json={"account": account, "password": password})
    if response.status_code == 409:
        response = client.post("/api/auth/login", json={"account": account, "password": password})
    response.raise_for_status()
    return response.json()


def main():
    alice = register_or_login("alice_care")
    bob = register_or_login("bob_care")
    alice_token, bob_token = alice["token"], bob["token"]
    client.put(
        "/api/care/profile",
        json={"nickname": "念"},
        headers=auth(alice_token),
    ).raise_for_status()
    client.put(
        "/api/care/profile",
        json={"nickname": "安"},
        headers=auth(bob_token),
    ).raise_for_status()

    group = client.get("/api/care/group", headers=auth(alice_token)).json()
    if not group.get("in_group"):
        group = client.post(
            "/api/care/group/create",
            json={"password": "1234"},
            headers=auth(alice_token),
        ).json()
    code = group["group"]["invite_code"]

    bob_group = client.get("/api/care/group", headers=auth(bob_token)).json()
    if not bob_group.get("in_group"):
        response = client.post(
            "/api/care/group/join",
            json={"invite_code": code, "relation": "伴侣", "password": "1234"},
            headers=auth(bob_token),
        )
        response.raise_for_status()
        # 5.0.1 起带密码的关心组需要组长审批：alice 取 pending 申请并 approve。
        alice_view = client.get("/api/care/group", headers=auth(alice_token)).json()
        for request in alice_view.get("requests", []):
            if request.get("account") == bob["account"]:
                client.post(
                    f"/api/care/group/requests/{request['id']}/approve",
                    headers=auth(alice_token),
                ).raise_for_status()
        bob_group = client.get("/api/care/group", headers=auth(bob_token)).json()
    if bob_group.get("partner") is None:
        raise SystemExit("bob did not join the group")

    # Bob 的位置在西湖附近，给 App 一个真实对方坐标
    client.post(
        "/api/care/presence",
        json={
            "lat": 30.2741,
            "lon": 120.1551,
            "status": "STUDYING",
            "activity_note": "正在图书馆自习",
            "battery": 76,
            "device_type": "PHONE",
            "mood_emoji": "🌙",
            "mood_message": "晚安，早点休息",
        },
        headers=auth(bob_token),
    ).raise_for_status()

    today = date.today().isoformat()
    client.post(
        "/api/care/checkins/toggle",
        json={"date": today, "checked": True, "note": "背完单词"},
        headers=auth(bob_token),
    ).raise_for_status()

    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    existing = client.get(
        "/api/care/reminders",
        params={"start": today, "end": tomorrow},
        headers=auth(alice_token),
    ).json()["reminders"]
    if not any(r["title"] == "一起背单词" for r in existing):
        client.post(
            "/api/care/reminders",
            json={
                "date": today,
                "time_minutes": 20 * 60,
                "title": "一起背单词",
                "note": "20:00 图书馆",
            },
            headers=auth(alice_token),
        ).raise_for_status()

    # 让 App 通过正确的账号进入关心组
    alice_group = client.get("/api/care/group", headers=auth(alice_token)).json()
    print(
        json.dumps(
            {
                "base": BASE,
                "alice_account": alice["account"],
                "alice_password": "123456",
                "bob_account": bob["account"],
                "bob_password": "123456",
                "bob_token": bob_token,
                "invite_code": code,
                "partner": alice_group.get("partner"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    sys.exit(main())
````

### `server/tests/test_care_api.py`

> 关心组主流程接口测试（TestClient）。

````python
r"""关心组 / 状态 / 打卡 / 提醒 / 关心消息接口集成测试（5.0.1 建组密码 + 组长审批流程）。

前置（PowerShell，仓库根目录执行）：
    $db = Join-Path $env:TEMP "toughmind-care-test.db"
    Remove-Item $db, "$db-wal", "$db-shm" -ErrorAction SilentlyContinue
    $env:DB_PATH = $db
    Push-Location server\backend
    ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010
    # 服务就绪后另开终端，在仓库根目录执行：
    server\.venv\Scripts\python.exe server\tests\test_care_api.py
"""

import sys
import time
from datetime import date

import httpx

BASE = "http://127.0.0.1:8010"
client = httpx.Client(base_url=BASE, timeout=10, headers={"X-App-Version": "5.0.1"})


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def post(path, body=None, token=None):
    response = client.post(path, json=body, headers=auth(token) if token else None)
    assert response.status_code < 300, f"POST {path} -> {response.status_code} {response.text}"
    return response.json()


def get(path, token=None, params=None):
    response = client.get(path, params=params, headers=auth(token) if token else None)
    assert response.status_code < 300, f"GET {path} -> {response.status_code} {response.text}"
    return response.json()


def patch(path, body, token):
    response = client.patch(path, json=body, headers=auth(token))
    assert response.status_code < 300, f"PATCH {path} -> {response.status_code} {response.text}"
    return response.json()


def delete(path, token):
    response = client.delete(path, headers=auth(token))
    assert response.status_code < 300, f"DELETE {path} -> {response.status_code} {response.text}"
    return response.json()


def register(prefix):
    account = f"{prefix}{int(time.time() * 1000) % 10_000_000}"
    data = post("/api/auth/register", {"account": account, "password": "123456"})
    assert data["account"] == account and data["token"]
    return data


today = date.today().isoformat()
alice = register("alice")
bob = register("bob")
alice_token, bob_token = alice["token"], bob["token"]

# 1. 创建关心组（5.0.1 起必须设置至少 4 位验证密码）
created = post("/api/care/group/create", {"password": "1234"}, token=alice_token)
assert created["in_group"] is True
assert created["group"]["has_password"] is True
code = created["group"]["invite_code"]
assert len(code) == 6
print("group created:", code)

# 2. 申请加入关心组：带密码只产生 pending，需要组长审批
joined = post(
    "/api/care/group/join",
    {"invite_code": code, "relation": "伴侣", "password": "1234"},
    token=bob_token,
)
assert joined["in_group"] is False
assert joined["pending"] is True
assert joined["message"]
print("join pending:", joined["message"])

pending_requests = get("/api/care/group", token=alice_token)["requests"]
assert [r["account"] for r in pending_requests] == [bob["account"]]
assert pending_requests[0]["relation"] == "伴侣"
approved = post(
    f"/api/care/group/requests/{pending_requests[0]['id']}/approve",
    token=alice_token,
)
assert approved["in_group"] is True
assert approved["requests"] == []

# 审批后组员重新读取关心组才会 in_group: true
bob_view = get("/api/care/group", token=bob_token)
assert bob_view["in_group"] is True
assert bob_view["pending"] is False
assert bob_view["me"]["relation"] == "伴侣"
partner = bob_view["partner"]
assert partner is not None and partner["account"] == alice["account"]
assert partner["relation"] == "我"
alice_view = get("/api/care/group", token=alice_token)
assert alice_view["in_group"] is True
assert alice_view["partner"]["account"] == bob["account"]
print("joined partner:", partner["nickname"])

# 3. 状态上报 / 读取
post(
    "/api/care/presence",
    {
        "lat": 30.2741,
        "lon": 120.1551,
        "status": "STUDYING",
        "activity_note": "正在图书馆自习",
        "battery": 76,
        "device_type": "PHONE",
    },
    token=alice_token,
)
post(
    "/api/care/presence",
    {
        "lat": 30.2860,
        "lon": 120.1640,
        "status": "WORKING",
        "activity_note": "在忙工作",
        "battery": 62,
        "device_type": "PHONE",
    },
    token=bob_token,
)
presence = get("/api/care/presence", token=bob_token)
assert presence["partner"]["account"] == alice["account"]
assert presence["partner"]["presence"]["status"] == "STUDYING"
assert presence["partner"]["distance_m"] is not None
print("partner status:", presence["partner"]["presence"]["status"], "distance:", presence["partner"]["distance_m"])

# 4. 双人打卡
post("/api/care/checkins/toggle", {"date": today, "checked": True, "note": "背完单词"}, token=alice_token)
day_payload = get("/api/care/checkins", token=bob_token, params={"start": today, "end": today})
assert len(day_payload["records"]) == 1
assert day_payload["records"][0]["is_self"] is False
post("/api/care/checkins/toggle", {"date": today, "checked": True}, token=bob_token)
both = get("/api/care/checkins", token=alice_token, params={"start": today, "end": today})
assert len(both["records"]) == 2
print("check-in records:", len(both["records"]))

# 5. 共享提醒
reminder = post(
    "/api/care/reminders",
    {"date": today, "time_minutes": 20 * 60, "title": "一起背单词", "note": "20:00 图书馆"},
    token=alice_token,
)["reminder"]
assert reminder["is_mine"] is True
bob_reminders = get("/api/care/reminders", token=bob_token, params={"start": today, "end": today})["reminders"]
assert len(bob_reminders) == 1 and bob_reminders[0]["is_mine"] is False
patch(f"/api/care/reminders/{reminder['id']}", {"enabled": False}, token=bob_token)
alice_reminders = get("/api/care/reminders", token=alice_token, params={"start": today, "end": today})["reminders"]
assert alice_reminders[0]["enabled"] is False
print("shared reminder:", alice_reminders[0]["title"], "enabled:", alice_reminders[0]["enabled"])

# 6. 关心消息
post("/api/care/nudge", {"message": "别太累，记得喝水"}, token=alice_token)
nudges = get("/api/care/nudges", token=bob_token, params={"since_id": 0})["nudges"]
assert len(nudges) == 1 and nudges[0]["message"] == "别太累，记得喝水"
print("nudge:", nudges[0]["from_nickname"], "->", nudges[0]["message"])

# 7. 退出关心组
delete("/api/care/reminders/%s" % reminder["id"], token=alice_token)
post("/api/care/group/leave", token=bob_token)
after = get("/api/care/group", token=alice_token)
assert after["partner"] is None
assert get("/api/care/group", token=bob_token)["in_group"] is False
print("leave group ok")
print("ALL BACKEND TESTS PASSED")
````

### `server/tests/test_device_members.py`

> 设备成员、绑定与解绑测试。

````python
r"""ESP32 设备成员接口集成测试（5.0.1 建组密码 + 组长审批流程）。

前置（PowerShell，仓库根目录执行）：
    $db = Join-Path $env:TEMP "toughmind-devices-test.db"
    Remove-Item $db, "$db-wal", "$db-shm" -ErrorAction SilentlyContinue
    $env:DB_PATH = $db
    Push-Location server\backend
    ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010
    # 服务就绪后另开终端，在仓库根目录执行：
    server\.venv\Scripts\python.exe server\tests\test_device_members.py
"""

import time

import httpx

BASE = "http://127.0.0.1:8010"
DEVICE_SECRET = "toughmind_dms_hmac_key_2025"
client = httpx.Client(base_url=BASE, timeout=10, headers={"X-App-Version": "5.0.1"})


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def request(method, path, body=None, token=None, headers=None, expect=200):
    merged = dict(headers or {})
    if token:
        merged["Authorization"] = f"Bearer {token}"
    response = client.request(method, path, json=body, headers=merged)
    assert response.status_code == expect, (
        f"{method} {path} -> {response.status_code} {response.text} (expect {expect})"
    )
    return response.json()


def register(prefix):
    account = f"{prefix}{int(time.time() * 1000) % 10_000_000}"
    data = request("POST", "/api/auth/register", {"account": account, "password": "123456"})
    assert data["token"]
    return data


alice = register("da")
bob = register("db")
carol = register("dc")
alice_token, bob_token, carol_token = alice["token"], bob["token"], carol["token"]

# 1. 两人关心组（5.0.1：建组要密码，入组要组长审批）
group = request("POST", "/api/care/group/create", {"password": "1234"}, token=alice_token)
assert group["in_group"] is True
assert group["group"]["has_password"] is True
code = group["group"]["invite_code"]
assert len(code) == 6

joined = request(
    "POST",
    "/api/care/group/join",
    {"invite_code": code, "relation": "伴侣", "password": "1234"},
    token=bob_token,
)
assert joined["in_group"] is False
assert joined["pending"] is True

pending_requests = request("GET", "/api/care/group", token=alice_token)["requests"]
assert [r["account"] for r in pending_requests] == [bob["account"]]
assert pending_requests[0]["relation"] == "伴侣"
request(
    "POST",
    f"/api/care/group/requests/{pending_requests[0]['id']}/approve",
    token=alice_token,
)
bob_view = request("GET", "/api/care/group", token=bob_token)
assert bob_view["in_group"] is True
assert bob_view["partner"]["account"] == alice["account"]
print("group:", code)

# 2. App 端用邀请码把 ESP32 加进关心组
joined_device = request(
    "POST",
    "/api/care/devices/join",
    {"invite_code": code, "device_id": "esp32s3_toughmind_01", "device_name": "车机", "relation": "车载设备"},
    token=alice_token,
)
assert joined_device["ok"] is True
assert joined_device["device"]["device_id"] == "esp32s3_toughmind_01"
assert joined_device["device_token"] == ""
device_account = joined_device["device"]["account"]
print("device joined:", device_account)

# 3. 对方读取关心组：设备出现在 devices 与 members，且不抢占 partner
view = request("GET", "/api/care/group", token=bob_token)
assert view["in_group"] is True
assert view["partner"]["account"] == alice["account"], view["partner"]
assert view["partner"].get("is_device") is False
assert len(view["devices"]) == 1
assert view["devices"][0]["device_id"] == "esp32s3_toughmind_01"
assert any(m["account"] == device_account and m["is_device"] for m in view["members"])
print("members:", [(m["nickname"], m["is_device"]) for m in view["members"]])

# 4. App 代设备上报 presence（用户 Token）
request(
    "POST",
    f"/api/care/devices/esp32s3_toughmind_01/presence",
    {"lat": 30.2741, "lon": 120.1551, "status": "DRIVING", "activity_note": "车速 48 km/h", "battery": 100},
    token=bob_token,
)
view = request("GET", "/api/care/group", token=alice_token)
device = next(d for d in view["devices"] if d["device_id"] == "esp32s3_toughmind_01")
assert device["presence"]["status"] == "DRIVING"
assert device["presence"]["device_type"] == "ESP32"
assert device["presence"]["online"] is True
print("device presence:", device["presence"]["status"], device["presence"]["activity_note"])

# 4.1 App 加过的设备再自己来换 Token：应补发 device_token
device_self = request(
    "POST",
    "/api/care/devices/join",
    {
        "invite_code": code,
        "device_id": "esp32s3_toughmind_01",
        "device_name": "车机",
        "device_secret": DEVICE_SECRET,
    },
)
assert device_self["device_token"]
request(
    "POST",
    "/api/care/devices/esp32s3_toughmind_01/presence",
    {"lat": 30.27, "lon": 120.15, "status": "ONLINE", "battery": 100},
    headers={"X-Device-Token": device_self["device_token"]},
)
print("device token issued for app-added device")

# 5. ESP32 自加入：邀请码 + device_secret 换取 device_token
self_join = request(
    "POST",
    "/api/care/devices/join",
    {
        "invite_code": code,
        "device_id": "esp32s3_cabin_02",
        "device_name": "客厅设备",
        "device_secret": DEVICE_SECRET,
    },
)
token = self_join["device_token"]
assert token
request(
    "POST",
    "/api/care/devices/esp32s3_cabin_02/presence",
    {"lat": 30.28, "lon": 120.16, "status": "RESTING", "battery": 88},
    headers={"X-Device-Token": token},
)
# 错误 token 被拒绝
request(
    "POST",
    "/api/care/devices/esp32s3_cabin_02/presence",
    {"lat": 0, "lon": 0},
    headers={"X-Device-Token": "bad-token"},
    expect=403,
)
# 错误邀请码 / 错误设备密钥被拒绝
request(
    "POST",
    "/api/care/devices/join",
    {"invite_code": "ZZZZZZ", "device_id": "x", "device_secret": DEVICE_SECRET},
    expect=404,
)
request(
    "POST",
    "/api/care/devices/join",
    {"invite_code": code, "device_id": "x", "device_secret": "wrong"},
    expect=403,
)
print("self-join token ok")

# 6. 设备不占用两人名额：组里已有 2 位成员 + 2 台设备
view = request("GET", "/api/care/group", token=alice_token)
assert len(view["devices"]) == 2
assert len([m for m in view["members"] if not m["is_device"]]) == 2

# 7. 同一设备不能被第二个关心组抢走
carol_group = request(
    "POST", "/api/care/group/create", {"password": "1234"}, token=carol_token
)
assert carol_group["in_group"] is True
carol_code = carol_group["group"]["invite_code"]
request(
    "POST",
    "/api/care/devices/join",
    {"invite_code": carol_code, "device_id": "esp32s3_toughmind_01", "device_name": "车机"},
    token=carol_token,
    expect=409,
)

# 8. 非法设备 ID
request(
    "POST",
    "/api/care/devices/join",
    {"device_id": "bad id!", "device_secret": DEVICE_SECRET, "invite_code": code},
    expect=400,
)

# 9. 移除设备
request("DELETE", "/api/care/devices/esp32s3_cabin_02", token=alice_token)
view = request("GET", "/api/care/group", token=bob_token)
assert [d["device_id"] for d in view["devices"]] == ["esp32s3_toughmind_01"]
print("device removed, remaining:", [d["device_id"] for d in view["devices"]])

print("ALL DEVICE MEMBER TESTS PASSED")
````

---

返回索引：[README.md](02-实战库/项目/安卓应用开发/README.md)
