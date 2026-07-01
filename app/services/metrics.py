"""
数据分析与指标计算模块。

提供纯 Python 实现的统计函数，不依赖数据库。
所有函数接收字典列表（rows），返回聚合后的统计结果。

职责划分：
- 业务逻辑层（api.py）负责调度和组装
- 本层负责纯数据计算，便于单元测试
"""

from collections import Counter, defaultdict
from datetime import date, datetime


def build_overview(rows: list[dict]) -> dict:
    """
    构建首页概览卡片数据。

    计算指标：
    - total_records: 天气记录总条数
    - total_cities:  去重后的城市数量
    - highest_temp:  全部数据中最高温的最大值
    - lowest_temp:   全部数据中最低温的最小值

    Args:
        rows: 全部天气记录列表，每条需包含 city_name, high_temp, low_temp

    Returns:
        包含四个概览指标的字典；rows 为空时返回全 0
    """
    if not rows:
        return {
            "total_records": 0,
            "total_cities": 0,
            "highest_temp": 0,
            "lowest_temp": 0,
        }

    return {
        "total_records": len(rows),
        # 用集合去重 → 统计不重复城市数
        "total_cities": len({row["city_name"] for row in rows}),
        "highest_temp": max(row["high_temp"] for row in rows),
        "lowest_temp": min(row["low_temp"] for row in rows),
    }


def build_weather_type_distribution(rows: list[dict]) -> list[dict]:
    """
    统计各天气类型出现的次数。

    用 collections.Counter 对 weather_type 字段做频次统计，
    结果可用于 ECharts 饼图或柱状图。

    Args:
        rows: 天气记录列表，每条需包含 weather_type

    Returns:
        [{"weather_type": "晴", "count": 500}, ...]
    """
    counter = Counter(row["weather_type"] for row in rows)
    return [
        {"weather_type": weather_type, "count": count}
        for weather_type, count in counter.items()
    ]


def build_temperature_trend(rows: list[dict], limit: int = 30) -> list[dict]:
    """
    计算近 N 天的每日平均最高温趋势。

    算法：
    1. 按日期分组，收集每天所有城市/站点的最高温
    2. 对每天的数值取平均
    3. 只返回最近 limit 天的数据

    Args:
        rows:  天气记录列表
        limit: 返回的天数上限，默认 30 天

    Returns:
        [{"weather_date": "2026-06-17", "avg_high_temp": 31.5}, ...]
        按日期升序排列
    """
    # 按日期分组，使用 defaultdict(list) 自动创建空列表
    grouped = defaultdict(list)
    for row in rows:
        grouped[_normalize_date(row["weather_date"])].append(row["high_temp"])

    trend = []
    # 取最近 limit 天
    for weather_date in sorted(grouped.keys())[-limit:]:
        values = grouped[weather_date]
        trend.append(
            {
                "weather_date": weather_date.isoformat(),
                # 当天所有城市最高温的平均值，保留两位小数
                "avg_high_temp": round(sum(values) / len(values), 2),
            }
        )
    return trend


def build_city_average_temperatures(rows: list[dict]) -> list[dict]:
    """
    计算每个城市的平均最高温和平均最低温。

    用于天气分析页面的 Top10 排行。

    算法：
    1. 按城市名分组
    2. 对每个城市分别计算 high_temp 和 low_temp 的平均值

    Returns:
        [{"city_name": "北京", "avg_high_temp": 25.3, "avg_low_temp": 12.1}, ...]
    """
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["city_name"]].append(row)

    averages = []
    for city_name, city_rows in grouped.items():
        num = len(city_rows)  # 该城市的数据条数
        averages.append(
            {
                "city_name": city_name,
                "avg_high_temp": round(
                    sum(row["high_temp"] for row in city_rows) / num, 2
                ),
                "avg_low_temp": round(
                    sum(row["low_temp"] for row in city_rows) / num, 2
                ),
            }
        )
    return averages


def build_province_average_temperatures(
    rows: list[dict], city_to_province: dict[str, str]
) -> list[dict]:
    """
    按省份聚合平均最高温（用于天气地图着色）。

    利用 city_to_province 映射表将城市级数据聚合到省份级。
    只统计能找到省份映射的城市；无法映射的忽略。

    Args:
        rows:             天气记录列表
        city_to_province: {城市名: 省份名} 的映射字典

    Returns:
        [{"province_name": "广东", "avg_high_temp": 30.2}, ...]
    """
    grouped = defaultdict(list)
    for row in rows:
        province_name = city_to_province.get(row["city_name"])
        if province_name:
            grouped[province_name].append(row["high_temp"])

    return [
        {
            "province_name": province_name,
            "avg_high_temp": round(sum(values) / len(values), 2),
        }
        for province_name, values in grouped.items()
    ]


def _normalize_date(value) -> date:
    """
    将各种日期格式统一转为 datetime.date 对象。

    支持的输入格式：
    - datetime.datetime 对象 → 取 .date()
    - datetime.date 对象    → 直接返回
    - 字符串 "YYYY-MM-DD"   → 解析后返回

    Args:
        value: 日期值（datetime、date 或 str）

    Returns:
        datetime.date 对象
    """
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()
