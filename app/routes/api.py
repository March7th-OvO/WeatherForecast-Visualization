"""
API 蓝图模块 —— 为前端 ECharts 图表提供 JSON 数据接口。

所有接口均返回 JSON 格式数据，不直接渲染 HTML。
前端通过 fetch() 或 jQuery Ajax 调用这些端点获取数据后，
再使用 ECharts 在浏览器中渲染图表。

接口一览：
    GET /api/dashboard   → 首页总览（概览卡片 + 趋势图 + 天气分布）
    GET /api/map         → 天气地图（各省平均最高温）
    GET /api/analysis    → 天气分析（高温 Top10、低温 Top10、类型占比）
    GET /api/history     → 15日天气查询（按城市名筛选 15 天预报明细）
"""

from urllib.parse import unquote

from flask import Blueprint, jsonify, request

from app.db import fetch_all_weather_rows
from app.services.metrics import (
    build_city_average_temperatures,
    build_overview,
    build_province_average_temperatures,
    build_temperature_trend,
    build_weather_type_distribution,
)
from spider.city_list import load_city_codes

# 创建 API 蓝图，所有路由自动加上 /api 前缀
api_bp = Blueprint("api", __name__, url_prefix="/api")


# =============================================================================
# 数据组装函数（供路由调用，也方便单元测试 mock）
# =============================================================================

def fetch_dashboard_payload() -> dict:
    """
    组装首页 Dashboard 所需的全部数据。

    包含三部分：
    1. overview: 总记录数、城市数、全局最高/最低温
    2. trend: 近 30 天每日平均最高温趋势
    3. weather_types: 各天气类型（晴、阴、雨等）的出现次数

    Returns:
        dict: 可直接 jsonify 的字典
    """
    rows = fetch_all_weather_rows()
    if not rows:
        # 无数据时返回空结构，前端据此展示"暂无数据"
        return {
            "overview": {
                "total_records": 0,
                "total_cities": 0,
                "highest_temp": 0,
                "lowest_temp": 0,
            },
            "trend": [],
            "weather_types": [],
        }

    return {
        "overview": build_overview(rows),
        "trend": build_temperature_trend(rows),
        "weather_types": build_weather_type_distribution(rows),
    }


def fetch_history_payload(city_name: str) -> list[dict]:
    """
    按城市名查询 15 日天气预报记录。

    查询逻辑：
    1. URL 解码城市名（处理中文参数）
    2. 在全部数据中精确匹配城市名
    3. 如果匹配不到，回退 (fallback) 到数据集中的第一个城市
       （避免默认值"北京"不在数据集中时返回空列表）

    Args:
        city_name: 来自 URL query string 的城市名（可能含 URL 编码）

    Returns:
        list[dict]: 该城市的 15 天预报记录，按日期降序排列
    """
    rows = fetch_all_weather_rows()
    # URL 解码 → 去除首尾空格
    normalized_city_name = unquote(str(city_name)).strip()

    # 第一轮：精确匹配用户输入的城市
    matched_rows = [
        _serialize_weather_row(row)
        for row in rows
        if str(row["city_name"]).strip() == normalized_city_name
    ]
    if matched_rows:
        return matched_rows

    # 第二轮：回退——取数据集中第一个城市
    if not rows:
        return []

    fallback_city_name = str(rows[0]["city_name"]).strip()
    return [
        _serialize_weather_row(row)
        for row in rows
        if str(row["city_name"]).strip() == fallback_city_name
    ]


# =============================================================================
# API 路由端点
# =============================================================================

@api_bp.get("/dashboard")
def dashboard_data():
    """首页总览数据接口"""
    return jsonify(fetch_dashboard_payload())


@api_bp.get("/map")
def map_data():
    """
    天气地图数据接口。

    返回各省份的平均最高温，前端 ECharts 结合 china.js 地理坐标
    在中国地图上按温度高低着色。
    """
    rows = fetch_all_weather_rows()

    # 加载城市元数据（包含城市→省份映射），上限 2000 个站点
    city_metadata = load_city_codes(2000)

    # 构建 {城市名: 省份名} 映射表，用于将城市级别数据聚合到省份级别
    city_to_province = {
        item["city_name"]: item["province_name"]
        for item in city_metadata
        if item.get("province_name")
    }

    return jsonify({
        "provinces": build_province_average_temperatures(rows, city_to_province)
    })


@api_bp.get("/analysis")
def analysis_data():
    """
    天气分析数据接口。

    返回：
    - high_top10: 平均最高温最高的 10 个城市
    - low_top10:  平均最低温最低的 10 个城市
    - weather_types: 天气类型分布统计
    """
    rows = fetch_all_weather_rows()

    # 先计算每个城市的平均最高温 / 最低温
    city_averages = build_city_average_temperatures(rows)

    # 按 avg_high_temp 降序排列取前 10 → 最热城市 Top10
    high_top10 = sorted(
        city_averages,
        key=lambda item: item["avg_high_temp"],
        reverse=True,
    )[:10]

    # 按 avg_low_temp 升序排列取前 10 → 最冷城市 Top10
    low_top10 = sorted(city_averages, key=lambda item: item["avg_low_temp"])[:10]

    return jsonify(
        {
            "high_top10": high_top10,
            "low_top10": low_top10,
            "weather_types": build_weather_type_distribution(rows),
        }
    )


@api_bp.get("/history")
def history_data():
    """
    15日天气查询接口。

    Query 参数:
        city_name: 城市名（可选，默认"北京"）

    示例:
        GET /api/history?city_name=上海
    """
    city_name = request.args.get("city_name", "北京")
    return jsonify(fetch_history_payload(city_name))


# =============================================================================
# 内部工具函数
# =============================================================================

def _serialize_weather_row(row: dict) -> dict:
    """
    序列化单条天气记录。

    如果 weather_date 是 datetime/date 对象（Pandas 读取后可能出现），
    调用 isoformat() 转为标准字符串，确保 JSON 序列化不报错。

    Args:
        row: 单条天气记录字典

    Returns:
        可安全 JSON 序列化的字典副本
    """
    serialized = dict(row)
    weather_date = serialized.get("weather_date")
    if hasattr(weather_date, "isoformat"):
        serialized["weather_date"] = weather_date.isoformat()
    return serialized
