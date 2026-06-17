from pathlib import Path

from app import create_app
from app.db import fetch_all_weather_rows


def test_fetch_all_weather_rows_reads_clean_csv(tmp_path):
    csv_path = tmp_path / "weather_clean_sample.csv"
    csv_path.write_text(
        "city_name,weather_date,weather_type,high_temp,low_temp,wind_level\n"
        "北京,2026-06-17,晴,31,21,<3级\n"
        "上海,2026-06-18,多云,29,23,<3级\n",
        encoding="utf-8-sig",
    )

    app = create_app()
    app.config["CLEAN_DATA_FILE"] = str(csv_path)

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
