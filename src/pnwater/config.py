from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PNWATER_", env_file=".env")

    database_url: str = "postgresql+psycopg://pnwater:pnwater@localhost:5432/pnwater"
    kafka_bootstrap_servers: str = "localhost:9092"

    simulator_interval_seconds: float = 2.0
    anomaly_z_score_warning: float = 2.5
    anomaly_z_score_critical: float = 4.0

    # Resolved relative to the current working directory, not the
    # installed package location -- train.py used to compute this with
    # Path(__file__).resolve().parents[3], which finds the repo root
    # when running from a source checkout but resolves to somewhere
    # under site-packages once the package is `pip install`-ed, which is
    # exactly what every Dockerfile here does. Run both training and the
    # services from the repo root (the Dockerfile's WORKDIR is /app,
    # where models/ is copied to, so this just works in containers).
    model_path: str = "models/anomaly_model.joblib"
    metrics_path: str = "models/metrics.json"

    # Empty by default: the alert agent falls back to a deterministic
    # templated message when no key is configured (see
    # services/alert_agent/llm.py). Never required for the app to start.
    google_api_key: str = ""


settings = Settings()
