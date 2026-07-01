"""
测试 db 模块 —— MySQL 数据读取与类型转换。

验证 fetch_all_weather_rows() 能够：
1. 使用 Flask 配置连接 MySQL
2. 从 weather_daily 表读取数据
3. 将 MySQL DATE 和数值字段整理为 API 约定格式
"""

from datetime import date
from unittest.mock import patch

from app import create_app
from app.db import fetch_all_weather_rows


class FakeCursor:
    """模拟 PyMySQL DictCursor，避免单元测试依赖真实 MySQL。"""

    def __init__(self, rows):
        self.rows = rows
        self.executed_sql = ""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def execute(self, sql):
        self.executed_sql = sql

    def fetchall(self):
        return self.rows


class FakeConnection:
    """模拟 PyMySQL connection，只覆盖当前测试需要的行为。"""

    def __init__(self, rows):
        self.rows = rows
        self.closed = False

    def cursor(self):
        return FakeCursor(self.rows)

    def close(self):
        self.closed = True


@patch("app.db.pymysql.connect")
def test_fetch_all_weather_rows_reads_mysql_rows(mock_connect):
    """
    验证从 MySQL 读取天气数据的完整流程。

    关键验证点：
    - DATE 对象会转成 YYYY-MM-DD 字符串
    - 温度值会转为 int
    - 连接参数来自 Flask app.config
    """
    mock_connect.return_value = FakeConnection(
        [
            {
                "city_name": "上海",
                "weather_date": date(2026, 6, 18),
                "weather_type": "多云",
                "high_temp": 29,
                "low_temp": 23,
                "wind_level": "<3级",
            },
            {
                "city_name": "北京",
                "weather_date": date(2026, 6, 17),
                "weather_type": "晴",
                "high_temp": 31,
                "low_temp": 21,
                "wind_level": "<3级",
            },
        ]
    )

    app = create_app()
    app.config.update(
        MYSQL_HOST="127.0.0.1",
        MYSQL_PORT=3306,
        MYSQL_USER="root",
        MYSQL_PASSWORD="123456",
        MYSQL_DATABASE="weather_visualization",
    )

    with app.app_context():
        rows = fetch_all_weather_rows()

    assert rows == [
        {
            "city_name": "上海",
            "weather_date": "2026-06-18",
            "weather_type": "多云",
            "high_temp": 29,
            "low_temp": 23,
            "wind_level": "<3级",
        },
        {
            "city_name": "北京",
            "weather_date": "2026-06-17",
            "weather_type": "晴",
            "high_temp": 31,
            "low_temp": 21,
            "wind_level": "<3级",
        },
    ]
    mock_connect.assert_called_once()
    assert mock_connect.call_args.kwargs["port"] == 3306
