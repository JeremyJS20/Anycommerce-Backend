from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvVariables(BaseSettings):
    port: str
    host: str
    mongodb_connection_string: str
    mongodb_database: str
    auth_secret_key: str
    origins: str
    stripe_secret_key: str
    countries_api_url: str
    countries_api_key: str
    currency_convertion_api_url: str
    app_api_key: str

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    @property
    def origins_list(self) -> list[str]:
        return [i.strip() for i in self.origins.split(",")]


env_variables = EnvVariables()
