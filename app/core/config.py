from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    BaseSettings reads environment variables (and from .env).
    We declare the three keys your service needs.
    Settings is now an object you can import anywhere to access those values.
    """
    finnhub_api_key: str
    database_url: str
    kafka_bootstrap_servers: str = ""
    database_url: str
    redis_url: str = ""
    redis_host: str = "localhost"
    redis_port: int = 6379

    class Config:
        env_file = ".env"

settings = Settings()
