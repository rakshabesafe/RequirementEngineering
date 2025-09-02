from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@postgres/ai_platform_db"

    # Jira Configuration
    # These should be set in the environment (e.g., in docker-compose.yml)
    JIRA_URL: str = "https://your-jira-instance.atlassian.net"
    JIRA_USERNAME: str = "your-email@example.com"
    JIRA_API_TOKEN: str = "your-api-token"

    class Config:
        # In a real app, you would use a .env file or environment variables
        # and not have default credentials in the code.
        pass

settings = Settings()
