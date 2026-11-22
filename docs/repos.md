# 本项目使用的真实仓库

选定于 2026-11-20。每条的用途不同，后面构造评测集时按这里的定位取数。

| 仓库 | 定位 | 用途 |
|---|---|---|
| `pandas-dev/pandas` | 大而杂，issue 量巨大，label 体系成熟 | 检索与标签基线的压力测试；重复 issue 极多 |
| `encode/httpx` | 中等活跃，维护者响应快，issue 描述规范 | 主评测集来源（100 条标签 + 100 对重复） |
| `Hello-Agents`（用户指定） | 中文 agent 项目，issue 少而贴近本项目主题 | 演示与中文场景验证（demo 默认仓库） |

## 取数约定

- 只取 public 仓库，用 `GITHUB_TOKEN` 只读权限。
- 每条 issue 保存：`number / title / body / state / labels / created_at / closed_at / html_url`。
- 重复样本只认 GitHub 的 `closed_as_duplicate_of` 事件（timeline API），不靠关键词猜。
- 抓取结果落 `data/triage.db`，`data/` 不进 git。

## 模型

- 渠道：DeepSeek（OpenAI 兼容），`LLM_BASE_URL=https://api.deepseek.com`，`LLM_MODEL=deepseek-chat`。
- M0 到 M5 一律用假模型（`FakeLLM`，确定性输出），M6 起才真正调用。
  理由：先把循环、工具面、评测口径跑对，再花钱换真实数字；否则调试期的花费会掩盖设计问题。