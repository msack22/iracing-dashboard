from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    iracing_username: str = ""
    iracing_password: str = ""
    iracing_customer_id: int = 1240652
    use_mock: bool = True
    port: int = 4001

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
