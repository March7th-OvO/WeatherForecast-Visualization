from app.services.metrics import build_overview


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
