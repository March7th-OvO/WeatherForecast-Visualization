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
