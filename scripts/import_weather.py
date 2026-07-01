"""
天气数据 MySQL 导入脚本（可选模块）。

将清洗后的 CSV 数据批量导入 MySQL 数据库的 weather_daily 表。

注意：
- 本项目当前以纯 CSV 模式运行为主，MySQL 是可选扩展
- 使用前确保本地 MySQL 已启动，并在 .env 中配置连接参数
- 表结构定义见 sql/schema.sql

用法：
    python -m scripts.import_weather
    python -m scripts.import_weather --input data/clean/weather_clean_xxx.csv
"""

import argparse
import os
from pathlib import Path

import pandas as pd
import pymysql


def import_clean_csv_to_mysql(input_path: Path, mysql_config: dict) -> int:
    """
    将清洗后的 CSV 逐行插入 MySQL。

    使用 ON DUPLICATE KEY UPDATE 策略：
    - 如果 (city_name, weather_date) 组合已存在 → 更新天气数据
    - 如果不存在 → 插入新行
    这样重复导入不会产生重复数据。

    Args:
        input_path:   清洗后 CSV 文件路径
        mysql_config: MySQL 连接参数字典，需包含 host/port/user/password/database

    Returns:
        实际插入的行数
    """
    frame = pd.read_csv(input_path)

    # 建立 MySQL 连接，autocommit=True 避免手动提交事务
    connection = pymysql.connect(
        host=mysql_config["host"],
        port=mysql_config["port"],
        user=mysql_config["user"],
        password=mysql_config["password"],
        database=mysql_config["database"],
        charset="utf8mb4",
        autocommit=True,
    )

    inserted = 0
    with connection.cursor() as cursor:
        # ON DUPLICATE KEY UPDATE：主键/唯一索引冲突时更新已有记录
        sql = """
        INSERT INTO weather_daily
        (city_name, weather_date, weather_type, high_temp, low_temp, wind_level)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            weather_type = VALUES(weather_type),
            high_temp = VALUES(high_temp),
            low_temp = VALUES(low_temp),
            wind_level = VALUES(wind_level)
        """
        for row in frame.to_dict(orient="records"):
            cursor.execute(
                sql,
                (
                    row["city_name"],
                    row["weather_date"],
                    row["weather_type"],
                    int(row["high_temp"]),
                    int(row["low_temp"]),
                    row["wind_level"],
                ),
            )
            inserted += 1

    connection.close()
    return inserted


def load_mysql_config() -> dict:
    """
    从环境变量读取 MySQL 连接配置。

    在 .env 文件中可配置以下变量（均有默认值）：
        MYSQL_HOST     默认 127.0.0.1
        MYSQL_PORT     默认 3306
        MYSQL_USER     默认 root
        MYSQL_PASSWORD 默认 123456
        MYSQL_DATABASE 默认 weather_visualization

    Returns:
        包含连接参数的字典
    """
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", "123456"),
        "database": os.getenv("MYSQL_DATABASE", "weather_visualization"),
    }


# =============================================================================
# 命令行入口
# =============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="将清洗后的天气 CSV 导入 MySQL")
    parser.add_argument("--input", type=str, default="", help="待导入的清洗 CSV 路径")
    args = parser.parse_args()

    # 自动选择最新的清洗 CSV
    input_path = (
        Path(args.input)
        if args.input
        else sorted(Path("data/clean").glob("weather_clean_*.csv"))[-1]
    )

    inserted = import_clean_csv_to_mysql(input_path, load_mysql_config())
    print(f"imported {inserted} rows from {input_path}")
