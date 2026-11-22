"""SQLite 访问层：连接、建表、事务。

为什么不用 ORM？
    本项目的查询只有三种：按 (repo, number) 查一条、按 repo 列表、插入或更新。
    ORM 在这个规模上只会增加一层需要学习的 API，而且 SQLite 的类型弱，
    ORM 帮不上忙。用原生 `sqlite3`，SQL 写在 `schema.sql` 里，可读、可 diff。
"""

from __future__ import annotations

import contextlib
import pathlib
import sqlite3
from typing import Iterator

from app.config import get_settings


def connect(db_path: str | pathlib.Path | None = None) -> sqlite3.Connection:
    path = pathlib.Path(db_path if db_path is not None else get_settings().db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row  # 可以按列名访问，例如row["id"]
    conn.execute("PRAGMA foreign_keys = ON")  # 为当前数据库连接启用外键约束检查
    conn.execute("PRAGMA journal_mode = WAL")  # 把数据库日志模式设置为Write-Ahead Logging:读操作和写操作可以更好地并发
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    sql = pathlib.Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()


# 事务生成器
@contextlib.contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    try:
        yield conn
    except BaseException:
        conn.rollback()
        raise
    else:
        conn.commit()
