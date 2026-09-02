from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://eventsphere:eventsphere@postgres:5432/payment_db"
    jwt_secret: str = "dev-insecure-secret-change-me"
    service_name: str = "payment-service"
    cors_origins: list[str] = ["http://localhost:3000"]
    booking_service_url: str = "http://booking-service:8000"

    # Razorpay TEST MODE credentials. Get these from
    # https://dashboard.razorpay.com/app/keys (toggle "Test Mode" on).
    # NEVER commit real values - see .env.example.
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_webhook_secret: str = ""
    currency: str = "INR"


settings = Settings()
