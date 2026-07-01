"""
测试 clean_weather 模块 —— 数据清洗逻辑。

核心测试目标：验证 normalize_row() 函数对字符串空格清理
和温度类型转换的正确性。
"""

from scripts.clean_weather import normalize_row


def test_normalize_row_converts_temperatures_and_trims_weather_type():
    """
    验证单行标准化清洗的正确性。

    输入：带前后空格、字符串类型的温度
    期望：空格被移除，温度转为 int 类型
    """
    row = {
        "city_name": "北京",
        "weather_date": "2026-01-01",
        "weather_type": " 小雨 ",      # ← 前后有空格
        "high_temp": "12",            # ← 字符串
        "low_temp": "3",              # ← 字符串
        "wind_level": " 3-4级 ",      # ← 前后有空格
    }

    normalized = normalize_row(row)

    assert normalized == {
        "city_name": "北京",
        "weather_date": "2026-01-01",
        "weather_type": "小雨",        # ← 空格已去除
        "high_temp": 12,              # ← 已转为 int
        "low_temp": 3,                # ← 已转为 int
        "wind_level": "3-4级",        # ← 空格已去除
    }
