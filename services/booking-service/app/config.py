from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://eventsphere:eventsphere@postgres:5432/booking_db"
    redis_url: str = "redis://redis:6379/0"
    jwt_secret: str = "dev-insecure-secret-change-me"
    service_name: str = "booking-service"
    cors_origins: list[str] = ["http://localhost:3000"]
    event_service_url: str = "http://event-service:8000"
    reservation_ttl_seconds: int = 600


settings = Settings()
