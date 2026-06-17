import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    def __init__(self) -> None:
        self.SECRET_KEY = os.getenv("SECRET_KEY", "weather-secret-key")
        self.RAW_DATA_DIR = str(BASE_DIR / "data" / "raw")
        self.CLEAN_DATA_DIR = str(BASE_DIR / "data" / "clean")
        self.CLEAN_DATA_FILE = os.getenv("CLEAN_DATA_FILE", "")
