import os

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

if os.environ.get("QUOTE_AQI_CONFIG_FILE"):
    toml_file = os.environ.get("QUOTE_AQI_CONFIG_FILE")
else:
    toml_file = "config.toml"


class Settings(BaseSettings):
    longitude: float
    latitude: float
    poi: str = ""

    caiyun_app_key: str
    caiyun_app_secret: str

    model_config = SettingsConfigDict(
        env_prefix="QUOTE_AQI_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            TomlConfigSettingsSource(settings_cls, toml_file=toml_file),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )
