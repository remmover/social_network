from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str = "SECRET_KEY"
    algorithm: str = "HS256"

    postgres_user: str = "POSTGRES_USER"
    postgres_password: str = "POSTGRES_PASSWORD"
    postgres_db: str = "POSTGRES_DB"
    postgres_host: str = "POSTGRES_HOST"
    postgres_port: int = 5432

    redis_host: str = "REDIS_HOST"
    redis_port: int = 6379
    redis_password: str = "REDIS_PASSWORD"

    mail_username: str = "HERO@meta.ua"
    mail_password: str = "HERO_MAILBOX_PASSWORD"
    mail_from: str = "HERO@meta.ua"
    mail_port: int = 465
    mail_server: str = "smtp.meta.ua"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


config = Settings()
