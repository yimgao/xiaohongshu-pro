"""配置管理 — Pydantic 驱动的类型安全配置。"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Browser ---
    headless: bool = False
    slow_mo: int = 100  # ms between actions
    viewport_width: int = 1280
    viewport_height: int = 800

    # --- LLM (for AI content gen) ---
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o"

    # --- Paths ---
    data_dir: Path = Field(default_factory=lambda: Path.cwd() / "data")
    cookie_file: Path | None = None  # computed below

    def model_post_init(self, __context) -> None:
        if self.cookie_file is None:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.cookie_file = self.data_dir / "cookies" / "xiaohongshu.json"
            self.cookie_file.parent.mkdir(parents=True, exist_ok=True)

    @property
    def llm_available(self) -> bool:
        return bool(self.llm_api_key)


settings = Settings()
