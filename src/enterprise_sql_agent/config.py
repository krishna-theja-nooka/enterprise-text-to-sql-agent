from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SQL_AGENT_", env_file=".env", extra="ignore")

    db_path: Path = Path("data/fleet_analytics.sqlite3")
    api_key: str = Field(default="", repr=False)
    requests_per_minute: int = Field(default=30, ge=1, le=300)
    max_rows: int = Field(default=100, ge=1, le=500)
