import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_db: str = "order_db"

    inventory_service_url: str = "http://127.0.0.1:5002"

    service_port: int = 5001

    class Config:
        env_prefix = "ORDER_"
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")


settings = Settings()
