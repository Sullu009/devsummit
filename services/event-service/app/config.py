from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://eventsphere:eventsphere@postgres:5432/event_db"
    jwt_secret: str = "dev-insecure-secret-change-me"
    service_name: str = "event-service"
    cors_origins: list[str] = ["http://localhost:3000"]
    identity_service_url: str = "http://identity-service:8000"


settings = Settings()
