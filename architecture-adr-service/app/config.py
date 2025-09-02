from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@postgres/ai_platform_db"

    class Config:
        pass

settings = Settings()
