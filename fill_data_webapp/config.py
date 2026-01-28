from datetime import datetime

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    db_host: str = Field(alias="POSTGRES_HOST", default="127.0.0.1")
    db_port: int = Field(alias="POSTGRES_PORT", default=5432)
    db_name: str = Field(alias="POSTGRES_DB")
    db_user: str = Field(alias="POSTGRES_USER")
    db_password: str = Field(alias="POSTGRES_PASSWORD")

    null_probability: float = 0.1
    min_int: int = 0
    max_int: int = 1_000_000
    min_float: float = 0
    max_float: float = 10_000
    float_precision: int = 2
    string_length: int = 255
    text_min_word_count: int = 2
    text_max_word_count: int = 30
    min_date: datetime = datetime(2000, 1, 1)

    batch_size: int = 10_000

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8")


settings = Settings()  # type: ignore
