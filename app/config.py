from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    CORS_ORIGINS: str = "http://localhost:5173"
    SECRET_KEY: str = "change_me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"
    

# Instantiate settings from environment or .env file. In CI/local use the DATABASE_URL env var or .env.
# Avoid hardcoding credentials here so runtime respects the docker/local DB settings.
settings = Settings()
