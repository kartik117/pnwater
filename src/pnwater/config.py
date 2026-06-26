from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PNWATER_", env_file=".env")

    database_url: str = "postgresql+psycopg://pnwater:pnwater@localhost:5432/pnwater"
    kafka_bootstrap_servers: str = "localhost:9092"

    simulator_interval_seconds: float = 2.0
    anomaly_z_score_warning: float = 2.5
    anomaly_z_score_critical: float = 4.0

    # Empty by default: the alert agent falls back to a deterministic
    # templated message when no key is configured (see
    # services/alert_agent/llm.py). Never required for the app to start.
    google_api_key: str = ""


settings = Settings()
