# issue-triage

开源仓库的 issue 分诊 agent：判重、打标签、起草回复，附一份可复算的评测报告。

## 状态

| 里程碑 | 内容 | 状态 |
|---|---|---|
| M0 | 仓库地基（配置、DB、领域模型、分层测试） | 进行中 |
| M1 | 抓取真实 issue | 未开始 |
| M2 | 评测集 | 未开始 |
| M3 | 检索 | 未开始 |
| M4 | 分诊 agent | 未开始 |
| M5 | API | 未开始 |
| M6 | 评测 | 未开始 |
| M7 | 部署 | 未开始 |
| M8 | 文档与演示 | 未开始 |

完整计划见 [PLAN.md](PLAN.md)。

## 快速开始

```powershell
cd E:\document\deepseek_folder\issue-triage
py -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env

py -m pytest tests -q
py scripts/init_db.py
```

## 目录

```text
app/
  config.py        配置（pydantic-settings）
  api/routes/      HTTP 路由
  core/            领域逻辑（不 import infra / api）
  infra/           DB、GitHub、模型客户端
  etl/             抓取与评测集构建
  eval/            指标与评测运行器
scripts/           一次性脚本
tests/             单元测试
data/              数据库与原始数据（不进 git）
outputs/           报告、trace（不进 git）
```