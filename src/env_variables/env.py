from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvVariables(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")


env_variables = EnvVariables()
