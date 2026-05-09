from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Translation Radar"
    environment: str = "development"
    debug: bool = True

    model_config = SettingsConfigDict(env_prefix="TRANSLATION_RADAR_", extra="ignore")


settings = Settings()