"""建库脚本：`py scripts/init_db.py`。

M0 的验收命令之一。它只做三件事：建目录、建表、打印各表行数。

## TODO(5)：实现 main

要求：
1. `from app.config import get_settings`，调 `ensure_dirs()` 拿到 db 路径。
2. `from app.infra.db import connect, init_schema`，连接后建表。
3. 打印一段可读信息：

       db: data/triage.db
       issues: 0 rows
       schema: ok

4. 用 `if __name__ == "__main__": main()` 守卫，让它可以被测试 import 而不执行。
5. 不要吞异常：建表失败就让它带着 traceback 退出（退出码非 0）。
"""

from __future__ import annotations

# TODO(5): 实现 main 与 __main__ 守卫
raise NotImplementedError("TODO(5): 实现 init_db.main")