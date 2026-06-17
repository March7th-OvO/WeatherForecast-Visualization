from app.services.metrics import build_overview, build_weather_type_distribution


def test_build_overview_returns_core_metrics():
    rows = [
        {"city_name": "北京", "high_temp": 10, "low_temp": 0},
        {"city_name": "上海", "high_temp": 12, "low_temp": 3},
    ]

    overview = build_overview(rows)

    assert overview == {
        "total_records": 2,
        "total_cities": 2,
        "highest_temp": 12,
        "lowest_temp": 0,
    }


def test_build_weather_type_distribution_counts_types():
    rows = [
        {"weather_type": "晴"},
        {"weather_type": "晴"},
        {"weather_type": "小雨"},
    ]

    assert build_weather_type_distribution(rows) == [
        {"weather_type": "晴", "count": 2},
        {"weather_type": "小雨", "count": 1},
    ]
