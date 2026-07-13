import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_db: str = "inventory_db"

    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    redis_db: int = 0

    service_port: int = 5002

    class Config:
        env_prefix = "INVENTORY_"
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")


settings = Settings()
