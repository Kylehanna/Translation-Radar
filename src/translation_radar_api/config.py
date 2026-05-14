from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Translation Radar"
    environment: str = "development"
    debug: bool = True
    rag_llm_api_url: str = ""
    rag_llm_api_key: str = ""
    rag_llm_model: str = ""
    rag_llm_timeout_seconds: int = 30

    model_config = SettingsConfigDict(env_prefix="TRANSLATION_RADAR_", extra="ignore")


settings = Settings()