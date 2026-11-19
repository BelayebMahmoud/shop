from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://shop:shop@localhost:5433/shop"
    jwt_secret: str = Field(min_length=32)  # required, no default: a missing or short secret stops startup
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30


settings = Settings()
