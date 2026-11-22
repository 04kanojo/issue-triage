"""分层约束测试：`core/` 不许依赖 `infra/` 与 `api/`。

为什么要用测试守架构？
    分层图贴在 README 里没人看，写进测试就会在 CI 与本地都红。
    规则只有一条，但它是这个项目能被讲清楚的前提：领域逻辑可以脱离网络与数据库单测。

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
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    # 广度遍历子树
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            # 一个节点可能导入多个: import os, sys
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # 相对导入，跳过
                continue
            if node.module:  # from . import x 时它是 None
                names.add(node.module)

    return names


def test_core_does_not_import_outer_layers() -> None:
    violations: list[str] = []

    for path in sorted(CORE_DIR.glob("*.py")):
        for name in _imports(path):
            if any(name == bad or name.startswith(bad + ".") for bad in FORBIDDEN):
                violations.append(f"{path.name}: {name}")

    assert not violations, "core 依赖了外层：\n" + "\n".join(violations)
