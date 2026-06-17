import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    def __init__(self) -> None:
        self.MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
        self.MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
        self.MYSQL_USER = os.getenv("MYSQL_USER", "root")
        self.MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "123456")
        self.MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "weather_visualization")
        self.SECRET_KEY = os.getenv("SECRET_KEY", "weather-secret-key")
        self.RAW_DATA_DIR = str(BASE_DIR / "data" / "raw")
        self.CLEAN_DATA_DIR = str(BASE_DIR / "data" / "clean")
