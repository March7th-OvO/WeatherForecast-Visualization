from unittest.mock import patch

from app import create_app


def test_health_route_returns_ok():
    app = create_app()
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_dashboard_page_renders_title():
    app = create_app()
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert "天气数据分析系统".encode("utf-8") in response.data


def test_map_analysis_and_history_pages_render():
    app = create_app()
    client = app.test_client()
    assert client.get("/map").status_code == 200
    assert client.get("/analysis").status_code == 200
    assert client.get("/history").status_code == 200


@patch("app.routes.api.fetch_dashboard_payload")
def test_dashboard_api_returns_overview(mock_payload):
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
