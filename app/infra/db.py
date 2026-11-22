"""SQLite 访问层：连接、建表、事务。

为什么不用 ORM？
    本项目的查询只有三种：按 (repo, number) 查一条、按 repo 列表、插入或更新。
    ORM 在这个规模上只会增加一层需要学习的 API，而且 SQLite 的类型弱，
    ORM 帮不上忙。用原生 `sqlite3`，SQL 写在 `schema.sql` 里，可读、可 diff。

## TODO(3)：connect 与 init_schema

    def connect(db_path: str | Path | None = None) -> sqlite3.Connection

要求：
1. `db_path` 为 None 时从 `app.config.get_settings().db_path` 取。
2. 父目录不存在则先 `mkdir(parents=True, exist_ok=True)`。
3. 连接后设置：
   - `row_factory = sqlite3.Row`（这样能 `row["title"]`）
   - `PRAGMA foreign_keys = ON`
   - `PRAGMA journal_mode = WAL`（读写并发更稳）
4. 返回连接对象。**不要** 在这里建表。

    def init_schema(conn: sqlite3.Connection) -> None

要求：
1. 读取与本文件同目录的 `schema.sql`（`pathlib.Path(__file__).with_name("schema.sql")`）。
2. `conn.executescript(sql)`，然后 `conn.commit()`。
3. 幂等：重复调用不报错（schema.sql 里已经用了 `IF NOT EXISTS`）。

## TODO(4)：transaction

    @contextlib.contextmanager
    def transaction(conn: sqlite3.Connection):
        ...

要求：
1. `yield conn`，正常结束时 `commit()`，任何异常时 `rollback()` 并把异常继续抛出。
2. 不要吞异常（吞掉会让调用方以为写成功了）。
3. 用 `try/except/else` 而不是 `try/finally`：`finally` 里 commit 会把异常路径也提交。
"""

from __future__ import annotations

import contextlib
import pathlib
import sqlite3

# TODO(3): 实现 connect 与 init_schema
raise NotImplementedError("TODO(3): 实现 connect 与 init_schema")

# TODO(4): 实现 transaction
# raise NotImplementedError("TODO(4): 实现 transaction")