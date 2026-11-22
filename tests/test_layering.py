"""分层约束测试：`core/` 不许依赖 `infra/` 与 `api/`。

为什么要用测试守架构？
    分层图贴在 README 里没人看，写进测试就会在 CI 与本地都红。
    规则只有一条，但它是这个项目能被讲清楚的前提：领域逻辑可以脱离网络与数据库单测。

## TODO(6)：实现 test_core_does_not_import_outer_layers

做法：
1. 用 `pathlib.Path(app_dir)` 遍历 `app/core/*.py`。
2. 对每个文件 `ast.parse` 源码，遍历 `ast.Import` 与 `ast.ImportFrom` 节点，
   取到完整模块名（`from app.infra.db import connect` 的模块名是 `app.infra.db`）。
3. 断言没有任何模块名等于或以 `app.infra` / `app.api` / `app.etl` 开头。
4. 收集违规（文件 + 模块名）后用 `assert not violations, ...` 一次报全，
   不要遇到第一个就 return。
5. 空列表也要能通过（现在 core 里只有 models.py 的桩）。

辅助：写一个 `_imports(path) -> set[str]` 函数，`ImportFrom` 的 `node.module` 可能为 None
（`from . import x` 这种相对导入），用 `node.level` 判断并跳过相对导入即可。

验收：`py -m pytest tests -q` 通过。
"""

from __future__ import annotations

import ast
import pathlib

APP_DIR = pathlib.Path(__file__).resolve().parent.parent / "app"
CORE_DIR = APP_DIR / "core"
FORBIDDEN = ("app.infra", "app.api", "app.etl")


def _imports(path: pathlib.Path) -> set[str]:
    """返回该文件 import 的完整模块名集合。"""
    raise NotImplementedError("TODO(6): 实现 _imports")


def test_core_does_not_import_outer_layers() -> None:
    raise NotImplementedError("TODO(6): 实现分层检查")