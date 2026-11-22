"""领域模型：`core/` 内部流通的纯数据。

为什么不用 dict？
    dict 的键名写错要到运行时才发现，而 dataclass 在构造时就能报错；
    而且类型注解让 IDE 和 `pytest` 都能帮忙。数据库行、API 请求、评测结果
    三处都用同一批对象，转换只在边界（infra / api）做。

## TODO(2)：实现三个 dataclass

全部用 `@dataclass(slots=True)`，字段与顺序如下（顺序参与 `==` 与 `repr`，别乱调）。

### Issue
    repo: str                  # "pandas-dev/pandas"
    number: int
    title: str
    body: str = ""
    state: str = "open"        # "open" | "closed"
    labels: list[str] = field(default_factory=list)
    created_at: str = ""       # ISO 8601 字符串，原样保存
    closed_at: str | None = None

要求：
- `labels` 必须用 `field(default_factory=list)`，不能写 `labels: list[str] = []`
  （共享可变默认值是 Python 最经典的坑之一）。
- 加 `@property def key(self) -> str: return f"{self.repo}#{self.number}"`。

### TriageResult
    repo: str
    number: int
    is_duplicate: bool = False
    duplicate_of: int | None = None
    labels: list[str] = field(default_factory=list)
    draft: str = ""
    confidence: float = 0.0
    cost_usd: float = 0.0
    latency_ms: int = 0
    trace_id: str = ""

要求：
- `to_dict()` 返回可 `json.dumps` 的 dict（字段名与上面一致）。

### Evaluation
    name: str                  # 基线名："rules" | "single_prompt" | "agent"
    n: int = 0
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    accuracy: float = 0.0
    macro_f1: float = 0.0
    cost_per_item: float = 0.0

要求：
- `to_dict()` 同上，保留三位小数（用 `round(x, 3)`）。
"""

from __future__ import annotations

from dataclasses import dataclass, field

# TODO(2): 在这里实现 Issue / TriageResult / Evaluation
raise NotImplementedError("TODO(2): 实现三个 dataclass")