import argparse
import os
from pathlib import Path

import pandas as pd
import pymysql


def import_clean_csv_to_mysql(input_path: Path, mysql_config: dict) -> int:
    frame = pd.read_csv(input_path)
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
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", "123456"),
        "database": os.getenv("MYSQL_DATABASE", "weather_visualization"),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="将清洗后的天气 CSV 导入 MySQL")
    parser.add_argument("--input", type=str, default="", help="待导入的清洗 CSV 路径")
    args = parser.parse_args()

    input_path = Path(args.input) if args.input else sorted(Path("data/clean").glob("weather_clean_*.csv"))[-1]
    inserted = import_clean_csv_to_mysql(input_path, load_mysql_config())
    print(f"imported {inserted} rows from {input_path}")
