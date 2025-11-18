from typing import Optional
#checking API
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    api_weather_key: str = Field("", env="API_WEATHER_KEY")
    # Timeout (seconds) to use for upstream API requests
    api_timeout: float = Field(10.0, env="API_TIMEOUT")
    default_lat: float = Field(47.6061, env = "DEFAULT_LAT")
    default_lon: float = Field(-122.3328, env = "DEFAULT_LON")
    units: str = Field("metric", env="WEATHER_UNITS")
    youtube_api_key: str = Field("", alias="API_YOUTUBE_KEY")
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"
settings = Settings()


# from typing import Optional
#
# from pydantic_settings import BaseSettings, SettingsConfigDict
# from pydantic import Field
#
#
# class Settings(BaseSettings):
#     model_config = SettingsConfigDict(
#         env_file=".env",
#         case_sensitive=False,
#         extra="ignore"
#     )
#
#     api_weather_key: str = Field("", env="API_WEATHER_KEY")
#     # Timeout (seconds) to use for upstream API requests
#     api_timeout: float = Field(10.0, env="API_TIMEOUT")
#     default_lat: float = Field(47.6061, env="DEFAULT_LAT")
#     default_lon: float = Field(-122.3328, env="DEFAULT_LON")
#     units: str = Field("metric", env="WEATHER_UNITS")
#     youtube_api_key: str = Field("", alias="API_YOUTUBE_KEY")
#
#
# settings = Settings()