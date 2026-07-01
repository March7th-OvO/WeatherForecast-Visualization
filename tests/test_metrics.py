"""
测试 metrics 模块 —— 数据聚合与统计计算。

所有指标计算函数均为纯函数（无副作用、无外部依赖），
测试只需准备输入数据并断言输出即可。
"""

from app.services.metrics import build_overview, build_weather_type_distribution


def test_build_overview_returns_core_metrics():
    """
    验证首页概览指标的计算逻辑。

    两个城市各一条记录 → total_records=2, total_cities=2
    """
    rows = [
        {"city_name": "北京", "high_temp": 10, "low_temp": 0},
        {"city_name": "上海", "high_temp": 12, "low_temp": 3},
    ]

    overview = build_overview(rows)

    assert overview == {
        "total_records": 2,
        "total_cities": 2,
        "highest_temp": 12,  # max(10, 12)
        "lowest_temp": 0,    # min(0, 3)
    }


def test_build_weather_type_distribution_counts_types():
    """
    验证天气类型频次统计。

    使用 collections.Counter 实现，结果按出现次数排列。
    """
    rows = [
        {"weather_type": "晴"},
        {"weather_type": "晴"},
        {"weather_type": "小雨"},
    ]

    assert build_weather_type_distribution(rows) == [
        {"weather_type": "晴", "count": 2},
        {"weather_type": "小雨", "count": 1},
    ]
