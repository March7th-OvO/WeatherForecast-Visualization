from pathlib import Path

import pandas as pd
from flask import current_app


def fetch_all_weather_rows():
    csv_path = _resolve_clean_data_file()
    if not csv_path or not csv_path.exists():
        return []

    frame = pd.read_csv(csv_path)
    if frame.empty:
        return []

    frame["weather_date"] = pd.to_datetime(frame["weather_date"], errors="coerce")
    frame["high_temp"] = pd.to_numeric(frame["high_temp"], errors="coerce")
    frame["low_temp"] = pd.to_numeric(frame["low_temp"], errors="coerce")
    frame = frame.dropna(subset=["weather_date", "high_temp", "low_temp"])
    frame = frame.sort_values("weather_date", ascending=False)
    frame["weather_date"] = frame["weather_date"].dt.strftime("%Y-%m-%d")
    frame["high_temp"] = frame["high_temp"].astype(int)
    frame["low_temp"] = frame["low_temp"].astype(int)

    return frame[
        [
            "city_name",
            "weather_date",
            "weather_type",
            "high_temp",
            "low_temp",
            "wind_level",
        ]
    ].to_dict(orient="records")


def _resolve_clean_data_file() -> Path | None:
    configured_path = current_app.config.get("CLEAN_DATA_FILE", "")
    if configured_path:
        return Path(configured_path)

    clean_dir = Path(current_app.config["CLEAN_DATA_DIR"])
    csv_files = sorted(clean_dir.glob("weather_clean_*.csv"))
    if not csv_files:
        return None
    return csv_files[-1]
