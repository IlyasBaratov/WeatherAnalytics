from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Pydantic Settings v2 uses `model_config` (not inner `Config`) for .env loading.
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    api_weather_key: str = Field(default="", validation_alias="API_WEATHER_KEY")
    api_ski_key: str = Field(default="", validation_alias="API_SKI_KEY")
    youtube_api_key: str = Field(default="", validation_alias="API_YOUTUBE_KEY")
    api_gemini_ai_key: str = Field(
        default="",
        validation_alias=AliasChoices("API_GEMINI_AI_KEY", "GEMINI_API_KEY"),
    )
    gemini_model: str = Field(default="gemini-2.5-flash", validation_alias="GEMINI_MODEL")

    # Timeout (seconds) to use for upstream API requests
    api_timeout: float = Field(default=10.0, validation_alias="API_TIMEOUT")
    default_lat: float = Field(default=47.6061, validation_alias="DEFAULT_LAT")
    default_lon: float = Field(default=-122.3328, validation_alias="DEFAULT_LON")
    units: str = Field(default="metric", validation_alias="WEATHER_UNITS")


settings = Settings()
