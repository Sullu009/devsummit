from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://eventsphere:eventsphere@postgres:5432/refund_db"
    jwt_secret: str = "dev-insecure-secret-change-me"
    service_name: str = "refund-service"
    cors_origins: list[str] = ["http://localhost:3000"]
    payment_service_url: str = "http://payment-service:8000"
    booking_service_url: str = "http://booking-service:8000"


settings = Settings()
