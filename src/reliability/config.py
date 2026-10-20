from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = "local"
    model_path: str = "artifacts/asset_risk_model.joblib"
    llm_provider: str = "disabled"
    openai_api_key: str | None = None
    openai_model: str | None = None
    max_agent_steps: int = 4

@lru_cache
def get_settings() -> Settings:
    return Settings()
