"""应用配置：把 `.env` 变成一个带类型的对象。

为什么需要它？
    代码里到处 `os.environ["LLM_API_KEY"]` 会带来三个问题：拼错名字要到运行时才炸、
    测试无法替换、默认值散落在各处。集中成一个 `Settings` 后，"缺哪个键"在启动时
    就报出来，测试里也能直接构造一个假的 Settings。
"""

from __future__ import annotations

import pathlib
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    def ensure_dirs(self) -> pathlib.Path:
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
