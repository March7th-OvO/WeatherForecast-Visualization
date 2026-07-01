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
        CLEAN_DATA_DIR:  清洗后 CSV 归档目录
        MYSQL_*:         MySQL 连接参数，Flask API 统一从数据库读取渲染数据
    """

    def __init__(self) -> None:
        # Flask 的 session / cookie 签名密钥，生产环境请改为随机字符串
        self.SECRET_KEY = os.getenv("SECRET_KEY", "weather-secret-key")

        # 数据目录：原始 CSV 和清洗后 CSV 分别存放；清洗 CSV 作为归档和导入源保留。
        self.RAW_DATA_DIR = str(BASE_DIR / "data" / "raw")
        self.CLEAN_DATA_DIR = str(BASE_DIR / "data" / "clean")

        # MySQL 连接配置：运行时 API 会直接查询 weather_daily 表，不再从 CSV 读取。
        self.MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
        self.MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
        self.MYSQL_USER = os.getenv("MYSQL_USER", "root")
        self.MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "123456")
        self.MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "weather_visualization")
