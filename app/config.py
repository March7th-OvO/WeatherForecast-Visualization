"""
应用配置模块。

负责从 .env 环境文件和系统环境变量中读取配置参数，
统一提供给 Flask 应用和其他模块使用。
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# ---- 项目根目录 ----
# app/config.py → app/ → 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 加载项目根目录下的 .env 文件，将其中的键值对注入到系统环境变量
# 这样 os.getenv() 就能读取到 .env 中定义的变量
load_dotenv(BASE_DIR / ".env")


class Config:
    """
    Flask 配置类。

    通过 from_object() 注入 Flask app.config 后，
    其他模块可通过 current_app.config 读取这些值。

    属性说明：
        SECRET_KEY:      Flask session 加密密钥
        RAW_DATA_DIR:    原始爬虫数据存放目录
        CLEAN_DATA_DIR:  清洗后数据存放目录
        CLEAN_DATA_FILE: 手动指定的清洗 CSV 路径；
                         若为空，系统自动选择 data/clean/ 下最新文件。
    """

    def __init__(self) -> None:
        # Flask 的 session / cookie 签名密钥，生产环境请改为随机字符串
        self.SECRET_KEY = os.getenv("SECRET_KEY", "weather-secret-key")

        # 数据目录：原始 CSV 和清洗后 CSV 分别存放
        self.RAW_DATA_DIR = str(BASE_DIR / "data" / "raw")
        self.CLEAN_DATA_DIR = str(BASE_DIR / "data" / "clean")

        # 手动指定的清洗数据文件路径（可选）
        # 例如在 .env 中写: CLEAN_DATA_FILE=data/clean/weather_clean_20260617_160504.csv
        self.CLEAN_DATA_FILE = os.getenv("CLEAN_DATA_FILE", "")
