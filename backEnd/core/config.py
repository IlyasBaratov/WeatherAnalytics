from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    api_weather_key: str = Field("", env="API_WEATHER_KEY")
    # Timeout (seconds) to use for upstream API requests
    api_timeout: float = Field(10.0, env="API_TIMEOUT")
    default_lat: float = Field(47.6061, env = "DEFAULT_LAT")
    default_lon: float = Field(-122.3328, env = "DEFAULT_LON")
    units: str = Field("metric", env="WEATHER_UNITS")
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"
settings = Settings()

# from pydantic_settings import BaseSettings, SettingsConfigDict
# from pydantic import Field
#
#
# class Settings(BaseSettings):
#     """
#     Application configuration for environment variables.
#     Uses pydantic-settings (Pydantic v2 compatible).
#     """
#
#     # 🌦️ OpenWeather API Key
#     api_weather_key: str = Field(
#         default="",
#         env="API_WEATHER_KEY",
#         description="Your OpenWeather API key."
#     )
#
#     # 📍 Default coordinates (Seattle by default)
#     default_lat: float = Field(
#         default=47.6061,
#         env="DEFAULT_LAT",
#         description="Default latitude if no location is provided."
#     )
#
#     default_lon: float = Field(
#         default=-122.3328,
#         env="DEFAULT_LON",
#         description="Default longitude if no location is provided."
#     )
#
#     # 🌡️ Units: metric (°C) or imperial (°F)
#     units: str = Field(
#         default="metric",
#         env="WEATHER_UNITS",
#         description="Measurement units for weather data."
#     )
#
#     # 🔧 Model configuration
#     model_config = SettingsConfigDict(
#         env_file=".env",
#         case_sensitive=False,
#         extra="ignore"
#     )
#
#
# # Create a singleton instance for import anywhere
# settings = Settings()
