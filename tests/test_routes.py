"""
测试 Flask 路由 —— 页面渲染和 API 响应。

使用 Flask 内置的 test_client() 发起模拟 HTTP 请求，
并通过 @patch 替换数据获取函数来隔离 MySQL 依赖。
"""

from unittest.mock import patch

from app import create_app


def test_health_route_returns_ok():
    """
    验证健康检查端点。

    GET /health 应返回 200 和 {"status": "ok"}，
    用于自动化运维检测服务状态。
    """
    app = create_app()
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_dashboard_page_renders_title():
    """
    验证首页 HTML 渲染。

    检查返回的 HTML 中是否包含页面标题"天气数据分析系统"。
    """
    app = create_app()
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert "天气数据分析系统".encode("utf-8") in response.data


def test_map_analysis_and_history_pages_render():
    """
    验证地图、分析、历史三个页面都能正常返回 200。

    页面渲染不依赖 MySQL 数据（数据由前端 AJAX 异步加载）。
    """
    app = create_app()
    client = app.test_client()

    # 地图页面应引用 china.js 中国地图地理数据
    map_response = client.get("/map")
    assert map_response.status_code == 200
    assert b"vendor/china.js" in map_response.data

    assert client.get("/analysis").status_code == 200
    assert client.get("/history").status_code == 200


@patch("app.routes.api.fetch_dashboard_payload")
def test_dashboard_api_returns_overview(mock_payload):
    """
    验证首页 Dashboard API（mock 数据）。

    @patch 替换 fetch_dashboard_payload 函数，
    避免测试依赖真实的 MySQL 服务。
    """
    mock_payload.return_value = {
        "overview": {
            "total_records": 20000,
            "total_cities": 100,
            "highest_temp": 38,
            "lowest_temp": -12,
        },
        "trend": [{"weather_date": "2026-01-01", "avg_high_temp": 12}],
        "weather_types": [{"weather_type": "晴", "count": 60}],
    }
    app = create_app()
    client = app.test_client()
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    assert response.get_json()["overview"]["total_records"] == 20000


@patch("app.routes.api.fetch_history_payload")
def test_history_api_returns_records(mock_history):
    """
    验证历史查询 API —— 按城市名筛选。

    传入 ?city_name=上海，期望返回该城市的天气数据。
    """
    mock_history.return_value = [
        {
            "city_name": "上海",
            "weather_date": "2026-01-01",
            "weather_type": "晴",
            "high_temp": 8,
            "low_temp": 1,
            "wind_level": "3级",
        }
    ]
    app = create_app()
    client = app.test_client()
    response = client.get("/api/history?city_name=上海")
    assert response.status_code == 200
    assert response.get_json()[0]["city_name"] == "上海"


@patch("app.routes.api.fetch_all_weather_rows")
def test_history_api_falls_back_to_first_city_when_default_city_missing(mock_rows):
    """
    验证历史查询的 fallback 逻辑。

    当默认城市（北京）不在数据集中时，
    API 应自动回退到数据集中的第一个城市（此处为"原阳"）。
    """
    mock_rows.return_value = [
        {
            "city_name": "原阳",
            "weather_date": "2026-07-01",
            "weather_type": "雨",
            "high_temp": 21,
            "low_temp": 18,
            "wind_level": "南风<3级",
        },
        {
            "city_name": "原阳",
            "weather_date": "2026-06-30",
            "weather_type": "阴转雨",
            "high_temp": 31,
            "low_temp": 20,
            "wind_level": "东南风<3级",
        },
    ]
    app = create_app()
    client = app.test_client()
    response = client.get("/api/history")
    assert response.status_code == 200
    assert response.get_json()[0]["city_name"] == "原阳"
