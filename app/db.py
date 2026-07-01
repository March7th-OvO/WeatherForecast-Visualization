"""
数据访问层模块（MySQL 模式）。

Flask API 统一从 MySQL 的 weather_daily 表读取清洗后的天气数据。
清洗 CSV 只作为数据归档和导入源，不再参与页面渲染时的数据读取。
"""

from datetime import date, datetime

import pymysql
from flask import current_app


def fetch_all_weather_rows() -> list[dict]:
    """
    从 MySQL 读取全部天气记录。

    查询结果保持 API 层原有的数据结构：
    - weather_date 格式化为 YYYY-MM-DD 字符串
    - high_temp / low_temp 转为 int
    - 按日期降序排列，保证最新天气优先展示

    Returns:
        list[dict]: 每项包含 city_name, weather_date, weather_type,
                    high_temp, low_temp, wind_level
    """
    connection = _connect_mysql()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    city_name,
                    weather_date,
                    weather_type,
                    high_temp,
                    low_temp,
                    wind_level
                FROM weather_daily
                ORDER BY weather_date DESC, city_name ASC
                """
            )
            rows = cursor.fetchall()
    finally:
        connection.close()

    return [_serialize_mysql_row(row) for row in rows]


def _connect_mysql():
    """
    创建 MySQL 连接。

    连接参数来自 Flask 配置对象，使用 DictCursor 让查询结果直接成为字典，
    便于 API 层沿用原有的 list[dict] 数据处理方式。
    """
    return pymysql.connect(
        host=current_app.config["MYSQL_HOST"],
        port=int(current_app.config["MYSQL_PORT"]),
        user=current_app.config["MYSQL_USER"],
        password=current_app.config["MYSQL_PASSWORD"],
        database=current_app.config["MYSQL_DATABASE"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def _serialize_mysql_row(row: dict) -> dict:
    """
    将 PyMySQL 查询结果整理成前端 API 约定格式。

    MySQL DATE 字段通常会被 PyMySQL 转为 datetime.date，这里统一输出为
    YYYY-MM-DD 字符串，避免 jsonify 序列化时出现环境差异。
    """
    weather_date = row["weather_date"]
    if isinstance(weather_date, datetime):
        weather_date = weather_date.date()
    if isinstance(weather_date, date):
        weather_date = weather_date.isoformat()

    return {
        "city_name": row["city_name"],
        "weather_date": str(weather_date),
        "weather_type": row["weather_type"],
        "high_temp": int(row["high_temp"]),
        "low_temp": int(row["low_temp"]),
        "wind_level": row["wind_level"],
    }
