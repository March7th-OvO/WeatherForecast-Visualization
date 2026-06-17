import pymysql
from flask import current_app


def get_connection():
    return pymysql.connect(
        host=current_app.config["MYSQL_HOST"],
        port=current_app.config["MYSQL_PORT"],
        user=current_app.config["MYSQL_USER"],
        password=current_app.config["MYSQL_PASSWORD"],
        database=current_app.config["MYSQL_DATABASE"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def fetch_all_weather_rows():
    try:
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT city_name, weather_date, weather_type, high_temp, low_temp, wind_level
                FROM weather_daily
                ORDER BY weather_date DESC
                """
            )
            rows = cursor.fetchall()
        connection.close()
        return rows
    except pymysql.MySQLError:
        return []
