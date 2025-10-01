from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    db_host: str = Field(alias="POSTGRES_HOST", default="127.0.0.1")
    db_port: int = Field(alias="POSTGRES_PORT", default=5432)
    db_name: str = Field(alias="POSTGRES_DB")
    db_user: str = Field(alias="POSTGRES_USER")
    db_password: str = Field(alias="POSTGRES_PASSWORD")

    model_config = ConfigDict(env_file="../.env", env_file_encoding="utf-8")


settings = Settings()
