"""应用配置：把 `.env` 变成一个带类型的对象。

为什么需要它？
    代码里到处 `os.environ["LLM_API_KEY"]` 会带来三个问题：拼错名字要到运行时才炸、
    测试无法替换、默认值散落在各处。集中成一个 `Settings` 后，"缺哪个键"在启动时
    就报出来，测试里也能直接构造一个假的 Settings。

## TODO(1)：实现 Settings 与 get_settings

字段（名字必须与 `.env.example` 完全一致，pydantic-settings 默认大小写不敏感）：

    github_token: str = ""
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com"
    llm_model: str = "deepseek-chat"
    db_path: str = "data/triage.db"

要求：
1. `class Settings(BaseSettings)`，用 `SettingsConfigDict(env_file=".env", extra="ignore")`
   让缺 `.env` 时也能启动（全部走默认值）。
2. 所有字段都有默认值，**任何字段都不允许在导入期抛异常**。
   理由：导入期抛错会让 `pytest` 在收集阶段就挂掉，而不是在某个用例里失败。
3. `get_settings()` 返回单例（用 `functools.lru_cache` 装饰），这样同一个进程里
   读到的配置一致；测试里可以 `get_settings.cache_clear()`。
4. 加一个只读属性 `has_llm`：`bool(self.llm_api_key)`。
   调用方用它决定"用真模型还是假模型"，不要到处判断空字符串。
5. 加一个方法 `ensure_dirs()`：确保 `db_path` 的父目录存在（`pathlib.Path.parent.mkdir`），
   返回该 `Path`。**不要**在 `__init__` 里建目录，副作用要显式调用。
"""

from __future__ import annotations

import pathlib
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


# TODO(1): 在这里补 Settings 类与 get_settings()
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding="utf-8")

    github_token: str = ""
    llm_base_url: str = "https://api.deepseek.com"
    llm_api_key: str = ""
    llm_model: str = "deepseek-flash"
    db_path: str = "data/triage.db"

    @property
    def has_llm(self) -> bool:
        return bool(self.llm_api_key)

    def ensure_dirs(self):
        parent = pathlib.Path(self.db_path).parent
        parent.mkdir(parents=True, exist_ok=True)
        return parent


# @lru_cache：让同一个进程里读到的配置一致，无论在哪调用都是同一个实例
@lru_cache
def get_settings() -> Settings:
    return Settings()


if __name__ == '__main__':
    s = get_settings()
    print(s.llm_model, s.db_path, s.has_llm)
    print(s.ensure_dirs())
    print(get_settings() is s)
