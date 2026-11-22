"""建库脚本：`py scripts/init_db.py`。

它只做三件事：建目录、建表、打印各表行数。
建表失败就让它带着 traceback 退出，不吞异常：（退出码非 0）。
"""
from __future__ import annotations
import pathlib
import sys
from contextlib import closing

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from app.config import get_settings
from app.infra.db import connect, init_schema


def main() -> None:
    # 1. 得到全局设置
    settings = get_settings()
    settings.ensure_dirs()
    print(f"db: {settings.db_path}")

    # 2. 初始化数据库
    with closing(connect(settings.db_path)) as conn:
        init_schema(conn)
        rows = conn.execute("SELECT COUNT(*) FROM issues").fetchone()[0]
    print(f"issues: {rows} rows")
    print("schema: ok")


if __name__ == "__main__":
    main()
