"""
天气数据 MySQL 导入脚本。

将清洗后的 CSV 数据批量写入 MySQL 的 weather_daily 表。
导入采用 upsert 策略，同一城市同一天的数据重复导入时会更新已有记录。

用法：
    python -m scripts.import_weather
    python -m scripts.import_weather --input data/clean/weather_clean_xxx.csv
    python -m scripts.import_weather --input data/clean/weather_clean_xxx.csv --skip-schema
"""

import argparse
import os
from pathlib import Path

import pandas as pd
import pymysql
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_DIR = BASE_DIR / "data" / "clean"

CREATE_WEATHER_DAILY_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS weather_daily (
    id INT PRIMARY KEY AUTO_INCREMENT,
    city_name VARCHAR(50) NOT NULL,
    weather_date DATE NOT NULL,
    weather_type VARCHAR(30) NOT NULL,
    high_temp INT NOT NULL,
    low_temp INT NOT NULL,
    wind_level VARCHAR(20) NOT NULL,
    UNIQUE KEY uniq_city_date (city_name, weather_date)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
"""


def import_clean_csv_to_mysql(
    input_path: Path,
    mysql_config: dict,
    ensure_schema: bool = True,
) -> int:
    """
    将清洗后的 CSV 批量 upsert 到 MySQL。

    Args:
        input_path:     清洗后 CSV 文件路径
        mysql_config:   MySQL 连接参数字典，需包含 host/port/user/password/database
        ensure_schema:  是否在导入前自动创建数据库和 weather_daily 表

    Returns:
        实际提交给 MySQL 的有效行数
    """
    if ensure_schema:
        ensure_database_and_table(mysql_config)

    rows = _read_clean_csv_rows(input_path)
    if not rows:
        return 0

    connection = _connect_mysql(mysql_config, include_database=True)
    try:
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO weather_daily
                (city_name, weather_date, weather_type, high_temp, low_temp, wind_level)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    weather_type = VALUES(weather_type),
                    high_temp = VALUES(high_temp),
                    low_temp = VALUES(low_temp),
                    wind_level = VALUES(wind_level)
                """,
                rows,
            )
        connection.commit()
    except Exception:
        _rollback_safely(connection)
        raise
    finally:
        connection.close()

    return len(rows)


def ensure_database_and_table(mysql_config: dict) -> None:
    """
    确保目标数据库和 weather_daily 表存在。

    这里不删除旧表，避免重新导入时误清空历史数据；唯一键负责处理重复记录。
    """
    database = mysql_config["database"]

    connection = _connect_mysql(mysql_config, include_database=False)
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{_escape_identifier(database)}` "
                "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            cursor.execute(f"USE `{_escape_identifier(database)}`")
            cursor.execute(CREATE_WEATHER_DAILY_TABLE_SQL)
        connection.commit()
    except Exception:
        _rollback_safely(connection)
        raise
    finally:
        connection.close()


def load_mysql_config() -> dict:
    """
    从 .env 和系统环境变量读取 MySQL 连接配置。

    可配置变量：
        MYSQL_HOST      默认 127.0.0.1
        MYSQL_PORT      默认 3306
        MYSQL_USER      默认 root
        MYSQL_PASSWORD  默认 123456
        MYSQL_DATABASE  默认 weather_visualization
    """
    load_dotenv(BASE_DIR / ".env")
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", "123456"),
        "database": os.getenv("MYSQL_DATABASE", "weather_visualization"),
    }


def _read_clean_csv_rows(input_path: Path) -> list[tuple]:
    """
    读取清洗 CSV，并再次做轻量类型校验。

    清洗脚本已经完成主要清洗；这里保留日期和温度校验，是为了避免手动传入的
    CSV 含有坏行时把非法数据写进 MySQL。
    """
    frame = pd.read_csv(input_path)
    if frame.empty:
        return []

    frame["weather_date"] = pd.to_datetime(frame["weather_date"], errors="coerce")
    frame["high_temp"] = pd.to_numeric(frame["high_temp"], errors="coerce")
    frame["low_temp"] = pd.to_numeric(frame["low_temp"], errors="coerce")
    frame = frame.dropna(
        subset=[
            "city_name",
            "weather_date",
            "weather_type",
            "high_temp",
            "low_temp",
            "wind_level",
        ]
    )

    return [
        (
            str(row["city_name"]).strip(),
            row["weather_date"].date(),
            str(row["weather_type"]).strip(),
            int(row["high_temp"]),
            int(row["low_temp"]),
            str(row["wind_level"]).strip(),
        )
        for row in frame.to_dict(orient="records")
    ]


def _resolve_clean_data_file(input_path: str) -> Path:
    """解析待导入的清洗 CSV 路径；未指定时使用 data/clean 下最新文件。"""
    if input_path:
        return Path(input_path)

    csv_files = sorted(CLEAN_DIR.glob("weather_clean_*.csv"))
    if not csv_files:
        raise FileNotFoundError("data/clean 目录下没有可导入的 weather_clean_*.csv 文件")
    return csv_files[-1]


def _connect_mysql(mysql_config: dict, include_database: bool):
    """创建 MySQL 连接；建库阶段不指定 database，导入阶段指定目标库。"""
    kwargs = {
        "host": mysql_config["host"],
        "port": int(mysql_config["port"]),
        "user": mysql_config["user"],
        "password": mysql_config["password"],
        "charset": "utf8mb4",
        "autocommit": False,
    }
    if include_database:
        kwargs["database"] = mysql_config["database"]
    return pymysql.connect(**kwargs)


def _escape_identifier(value: str) -> str:
    """转义 MySQL 标识符中的反引号，避免数据库名破坏 SQL 结构。"""
    return str(value).replace("`", "``")


def _rollback_safely(connection) -> None:
    """连接已被 MySQL 服务端断开时，rollback 可能失败；这里避免掩盖原始错误。"""
    try:
        connection.rollback()
    except pymysql.MySQLError:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="将清洗后的天气 CSV 导入 MySQL")
    parser.add_argument("--input", type=str, default="", help="待导入的清洗 CSV 路径")
    parser.add_argument(
        "--skip-schema",
        action="store_true",
        help="跳过自动建库建表，仅执行数据导入",
    )
    args = parser.parse_args()

    input_file = _resolve_clean_data_file(args.input)
    inserted = import_clean_csv_to_mysql(
        input_file,
        load_mysql_config(),
        ensure_schema=not args.skip_schema,
    )
    print(f"imported {inserted} rows from {input_file}")
