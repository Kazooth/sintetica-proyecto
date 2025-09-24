from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    CORS_ORIGINS: str = "http://localhost:5173"
    SECRET_KEY: str = "change_me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"


# Provide a safe default for type-checking; real value comes from env/.env in runtime/CI
settings = Settings(DATABASE_URL="postgresql+psycopg://user:pass@localhost:5432/postgres")
