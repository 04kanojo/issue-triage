"""领域模型：`core/` 内部流通的纯数据。

为什么不用 dict？
    dict 的键名写错要到运行时才发现，而 dataclass 在构造时就能报错；
    而且类型注解让 IDE 和 `pytest` 都能帮忙。数据库行、API 请求、评测结果
    三处都用同一批对象，转换只在边界（infra / api）做。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


# 抓下来的原始 issue，一条记录
@dataclass(slots=True)
class Issue:
    repo: str  # 仓库全名 "owner/name"；不同仓库的编号会重复，靠它区分
    number: int  # 该仓库内的 issue 编号（GitHub 的 #123），不是数据库自增 id
    title: str  # 标题；判重和打标签最强的文本信号，通常比正文还准
    body: str = ""  # 正文；有些 issue 只有标题，空串比 None 好处理
    state: str = "open"  # "open" | "closed"；抓取时原样保留，评测集按它过滤
    labels: list[str] = field(default_factory=list)  # 现有标签，是历史答案原料，不是模型输出
    created_at: str = ""  # 创建时间，ISO 8601 原文；不在 core 层解析时区
    closed_at: str | None = None  # 关闭时间；没关为 None，判重标注靠它做时间对齐

    @property
    def key(self) -> str:
        # repo#number：日志、报告、报错里要一个人类可读的主键
        return f"{self.repo}#{self.number}"


# agent 对一条 issue 的判决书
@dataclass(slots=True)
class TriageResult:
    repo: str  # 被分诊的仓库；结果要能指回输入，批量跑完才对得上号
    number: int  # 被分诊的 issue 编号
    is_duplicate: bool = False  # 是否判为重复；默认 False，没证据就不算重复
    duplicate_of: int | None = None  # 被重复的原 issue 编号；None 表示不是重复，别用 0/-1 代替
    labels: list[str] = field(default_factory=list)  # 建议标签（前 5 + other），顺序即优先级
    draft: str = ""  # 给报告人的回复草稿；不自动发送，人审后才回
    confidence: float = 0.0  # 0~1 置信度；低于阈值进人工复核队列，而不是直接判
    cost_usd: float = 0.0  # 这一次分诊花了多少钱；评测要算每条成本
    latency_ms: int = 0  # 耗时毫秒；汇总 P50/P95，只报均值会掩盖长尾
    trace_id: str = ""  # 关联 trace/日志的 id；出问题要能翻到那一轮的完整调用

    def to_dict(self) -> dict:
        return asdict(self)


# 一种基线在一份评测集上的成绩单
@dataclass(slots=True)
class Evaluation:
    name: str  # 基线名："rules" | "single_prompt" | "agent"
    n: int = 0  # 样本数；所有指标都要能配上分母
    precision: float = 0.0  # 查准率：判为重复的里面有多少真的重复（误判代价最高）
    recall: float = 0.0  # 查全率：真的重复里找到了多少（漏判会堆积重复 issue）
    f1: float = 0.0  # precision 与 recall 的调和平均；防止只刷单边
    accuracy: float = 0.0  # 标签整体准确率；直观但会被大类主导
    macro_f1: float = 0.0  # 各类 f1 的平均（不按样本量加权）；补 accuracy 的小类短板
    cost_per_item: float = 0.0  # 每条平均成本（美元）；和 f1 一起才是性价比

    def to_dict(self) -> dict:
        data = asdict(self)
        # float保留三位小数
        for key in ("precision", "recall", "f1", "accuracy", "macro_f1", "cost_per_item"):
            data[key] = round(data[key], 3)
        return data
