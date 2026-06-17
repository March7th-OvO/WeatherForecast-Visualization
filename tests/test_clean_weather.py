from scripts.clean_weather import normalize_row


def test_normalize_row_converts_temperatures_and_trims_weather_type():
    row = {
        "city_name": "北京",
        "weather_date": "2026-01-01",
        "weather_type": " 小雨 ",
        "high_temp": "12",
        "low_temp": "3",
        "wind_level": " 3-4级 ",
    }

    normalized = normalize_row(row)

    assert normalized == {
        "city_name": "北京",
        "weather_date": "2026-01-01",
        "weather_type": "小雨",
        "high_temp": 12,
        "low_temp": 3,
        "wind_level": "3-4级",
    }
