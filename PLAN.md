# issue-triage 学习计划

> 主项目：开源仓库的 issue 分诊 agent。这份文件是**教学大纲**，不是代码。
> 骨架项目 `bcefghj/ai-agent-interview-guide/project-python` 只借它的分层思路，一行都不复制。

## 0. 目标与验收

六周后仓库要能回答四个问题，且每个都有数字：

| 问题 | 验收物 |
|---|---|
| 分诊准不准？ | 100 条人工标注上，重复检测 F1 与标签准确率 |
| 比基线好在哪？ | 规则 / 单次 prompt / agent 三条基线的并列对比 |
| 能不能用？ | `POST /triage` 可用，P50 延迟与单条成本有数 |
| 别人能不能复现？ | `README.md` + `EVAL-REPORT.md`，新机器三条命令跑通 |

最终交付：代码 + 评测集 + 评测报告 + 一段 3 分钟演示（CLI 或网页）。

## 1. 技术选型

| 层 | 选 | 理由 |
|---|---|---|
| Web | FastAPI + Uvicorn | 骨架同款，生态最熟，自带 OpenAPI 文档 |
| 数据 | SQLite + 原生 `sqlite3` | 数据量 1 万条以内，零运维；**不用** PostgreSQL |
| 抓取 | httpx + tenacity | 重试与限流逻辑要自己写一遍 |
| 配置 | pydantic-settings | `.env` → 配置对象，类型错误启动即报 |
| 日志 | loguru | 一行接入结构化日志 |
| 检索 | `rank_bm25` + 可选向量 | 先纯 BM25 跑出基线，再证明向量有没有用 |
| Agent | 复用 `agent-cli/capstone` 的 loop 思想 | 但我们自己写一个更小的循环，不 import 老代码 |
| 部署 | Dockerfile + Compose（app + volume） | **不**塞 Milvus、Redis、etcd、minio |

明确不做：Milvus、Redis、LangChain、LangGraph、Kubernetes。理由统一一句话：**没有规模时不引入需要额外运维的组件**，面试时要能说出这句。

## 2. 目录结构（五层）

```text
issue-triage/
├── app/
│   ├── main.py                  # FastAPI 入口，只挂路由与启动钩子
│   ├── config.py                # pydantic-settings 配置
│   ├── api/
│   │   ├── deps.py              # 依赖注入：db 连接、LLM 客户端
│   │   └── routes/
│   │       ├── health.py
│   │       ├── issues.py        # 列表、详情
│   │       └── triage.py        # 分诊接口
│   ├── core/                    # 与框架无关的领域逻辑
│   │   ├── models.py            # dataclass：Issue / TriageResult / Evaluation
│   │   ├── search.py            # BM25 召回 + 融合排序
│   │   ├── dedupe.py            # 重复判定（规则 + 模型）
│   │   ├── label.py             # 标签预测
│   │   ├── draft.py             # 回复草稿
│   │   └── loop.py              # 小号 agent 循环（工具调用 + 预算）
│   ├── infra/
│   │   ├── db.py                # 连接、迁移、事务
│   │   ├── github.py            # GitHub REST 客户端
│   │   └── llm.py               # 模型客户端（OpenAI 兼容）
│   ├── etl/
│   │   ├── fetch_issues.py      # 抓取脚本
│   │   └── build_eval.py        # 从历史事件生成评测样本
│   └── eval/
│       ├── datasets.py          # 评测集加载
│       ├── metrics.py           # 精/召/F1、准确率、成本
│       └── run_eval.py          # 跑三条基线并出报告
├── scripts/
│   ├── init_db.py
│   └── seed_labels.py
├── tests/
├── data/                        # 不进 git（.gitignore）
├── outputs/                     # 报告、trace
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```

分层规则只有一条：**`core/` 不 import `infra/` 和 `api/`**。这条规矩用测试守（`tests/test_layering.py`），`core` 里的模块被 import 时不带副作用。

## 3. 里程碑与 TODO

每个里程碑是一个可独立验收的切片。**你要写的代码全部标 `TODO(n)`，我不会替你写；TODO 注释留在仓库里，你说删我才删。**

### M0 仓库地基（约 1.5 小时）

你要写：
- `pyproject.toml`：名称、Python 3.11、依赖、`[tool.ruff]`
- `.env.example`：`GITHUB_TOKEN`、`LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL`、`DB_PATH`
- `app/config.py`：`Settings(BaseSettings)`，字段与上面一一对应
- `app/infra/db.py`：`connect()`、`init_schema()`、`transaction()`
- `app/core/models.py`：三个 dataclass
- `scripts/init_db.py`：建表并打印行数
- `tests/test_layering.py`：断言 `core` 不引用 `infra`/`api`

验收：`py -m pytest tests -q` 通过；`py scripts/init_db.py` 后 `data/triage.db` 存在且 `issues` 表可查。

### M1 抓取真实 issue（约 2 小时）

你要写：
- `app/infra/github.py`：`list_issues(repo, state, page)`，带 `tenacity` 重试与分页
- `app/etl/fetch_issues.py`：CLI 参数 `--repo owner/name --limit 500`，入库去重（`(repo, number)` 唯一）
- 表：`issues`、`issue_labels`、`issue_links`（重复关系）

验收：`py -m app.etl.fetch_issues --repo ... --limit 500` 后表里有数据，重复跑不产生重复行。

### M2 评测集（约 3 小时）

你要写：
- `app/etl/build_eval.py`：从"被关闭为 duplicate"的事件反推正样本对；从同月随机抽取负样本对
- `data/eval_pairs.jsonl`（200 对，正负各 100）
- `data/eval_labels.jsonl`（100 条，人工确认过的标签）
- `scripts/seed_labels.py`：把标注写库

验收：`py -m app.etl.build_eval` 生成文件；随机抽 10 对人工看，正样本必须真的重复。

### M3 检索（约 3 小时）

你要写：
- `app/core/search.py`：`bm25_index(issues)`、`search(query, k)`、`fuse(bm25_hits, vec_hits)`
- 归一化、去停用词、代码块剥离（issue 正文里的堆栈会污染召回）

验收：给定 20 条已知重复对，`search` 的 top-5 命中率打印出来。

### M4 分诊 agent（约 4 小时，最重）

你要写：
- `app/core/loop.py`：`run(task, tools, budget)`，三段：发消息 → 执行工具 → 回填观察；错误回填不中断
- `app/core/dedupe.py`：工具集 `search_similar`、`read_issue`、`emit_verdict`
- `app/core/label.py`：工具集 `list_labels`、`emit_labels`
- `app/infra/llm.py`：OpenAI 兼容的 `complete(messages, tools)`，含 429 重试

验收：`py -m app.core.loop --issue 123` 输出结构化 verdict，trace 落到 `outputs/traces/`。

### M5 API（约 2 小时）

你要写：
- `app/api/routes/triage.py`：`POST /triage`（body: `repo`, `number`）、`GET /triage/{id}`
- `app/api/deps.py`：db 与 llm 的依赖
- Pydantic schema 与领域模型的转换

验收：`uvicorn app.main:app` 后 `curl` 两条命令返回 200，OpenAPI 页面能点。

### M6 评测（约 3 小时）

你要写：
- `app/eval/metrics.py`：`precision/recall/f1`、`accuracy`、`macro_f1`、`cost_per_item`
- `app/eval/run_eval.py`：三条基线（规则、单次 prompt、agent）+ 落 `outputs/report.json`
- 报告渲染 `outputs/report.md`

验收：`py -m app.eval.run_eval` 产出报告，三条基线的 F1 有差距且能解释。

### M7 部署（约 2 小时）

你要写：
- `Dockerfile`（多阶段，非 root 用户）
- `docker-compose.yml`（app + 挂载 data 卷）
- 一个定时任务脚本 `scripts/nightly.py`：抓新 issue 并批量分诊

验收：`docker compose up` 后 `/health` 返回 200，`data/` 挂载生效。

### M8 文档与演示（约 2 小时）

你要写：
- `README.md`：一句话、架构图（ASCII）、三条命令跑通、评测数字表
- `EVAL-REPORT.md`：数据来源、指标定义、三基线对比、错误分析 10 例
- `demo.py` 或一个静态页：输入仓库 + issue 号，打印分诊结果

验收：**在一台没装过本项目的机器上**按 README 跑通（可以让朋友试）。

总计约 22.5 小时，按每周 4 到 6 小时算，六周刚好。

## 4. TODO 约定

```python
# TODO(3): 实现分页抓取。要求：每页 100 条，遇 429 退避 1/2/4 秒，最多 3 次。
def list_issues(repo: str, state: str = "all", page: int = 1) -> list[dict]:
    raise NotImplementedError("TODO(3)")
```

- 编号全仓唯一，按里程碑顺序递增（M0 是 1 到 6）。
- 每条 TODO 的 docstring 里写死：输入、输出、边界条件、错误码。
- **不删**。只有你明确说"删掉 TODO(n)"我才删。
- 我验收时只跑命令看输出，不读你未提交的草稿。

## 5. 每节课的节奏（和 capstone 一致）

```text
1. 我先讲"这一步为什么存在"，给出它在架构里的位置
2. 我给 docstring 规格 + TODO 桩 + 一条验收命令（此时是红的）
3. 你写实现，卡住随时问，我只给提示不给答案
4. 你贴结果或我跑验收，我按 python-anti-patterns 清单逐条看
5. 绿了之后我讲"这段代码面试怎么被问"，更新 task_board 与进度
```

我会动用的 skill：

| 时机 | skill | 用它做什么 |
|---|---|---|
| 每次 review 代码 | `python-anti-patterns` | 逐条过清单，不凭印象说"写得不错" |
| 每个里程碑结束 | `code-review` | 需要 git 历史，所以 M0 就 `git init` 并每步 commit |
| M3、M6 | `python-performance-optimization` | BM25 建索引耗时、评测批量吞吐 |
| M8 | `technical-writing` | README 与评测报告按"读第二遍也不烦"的标准写 |
| 全程 | 不用 `build-project` | 它是课程 Projects 的引导器，与本项目无关 |

## 6. 数据与指标定义（先定，后跑）

- **重复对**：同一仓库内，后开的 issue 的 `closed_as_duplicate_of` 指向先开的。正样本只取这个事件，不靠关键词猜。
- **P（precision）**：判为重复且确实重复 / 判为重复的总数
- **R（recall）**：判为重复且确实重复 / 全部真重复
- **标签**：仓库真实 label 集合里取出现频次前 5 个，其余归 `other`
- **成本**：`(prompt_tokens × 输入价 + completion_tokens × 输出价)`，按当次模型单价记录
- **延迟**：单条从请求到返回的墙钟时间，报 P50 与 P95

## 7. 风险与裁剪

| 风险 | 应对 |
|---|---|
| 选中仓库没有 duplicate 标注 | 第 2 周发现就换仓库，别硬凑 |
| GitHub 限流（未登录 60 次/小时） | 必须配 token；抓取加缓存，落库后才分析 |
| 向量检索效果不明显 | 允许砍掉向量，只留 BM25，并在报告里写"为什么没用上" |
| 六周超期 | 优先保 M1/M2/M4/M6（数据、agent、评测），M7 可降级为"本地能起" |

## 8. 本周第一步

1. `git init`，建上面的目录骨架，把 `.gitignore` 里加 `data/`、`outputs/`、`.env`。
2. 你写 M0 的六个文件（我下一节课先给 docstring 与 TODO 桩）。
3. 三个人工练习：自己开一个测试仓库，造 5 条 issue，其中 2 条是重复，确认"重复"这件事在你选的标签体系里可判。