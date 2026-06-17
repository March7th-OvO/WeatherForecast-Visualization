from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/clean")


def normalize_row(row: dict) -> dict:
    return {
        "city_name": row["city_name"].strip(),
        "weather_date": row["weather_date"].strip(),
        "weather_type": row["weather_type"].strip(),
        "high_temp": int(str(row["high_temp"]).strip()),
        "low_temp": int(str(row["low_temp"]).strip()),
        "wind_level": row["wind_level"].strip(),
    }


def clean_csv(input_path: Path, output_path: Path) -> None:
    frame = pd.read_csv(input_path)
    cleaned_rows = [normalize_row(row) for row in frame.to_dict(orient="records")]
    cleaned_frame = pd.DataFrame(cleaned_rows).drop_duplicates(
        subset=["city_name", "weather_date"]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_frame.to_csv(output_path, index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    latest_file = sorted(RAW_DIR.glob("weather_raw_*.csv"))[-1]
    output_file = CLEAN_DIR / latest_file.name.replace("raw", "clean")
    clean_csv(latest_file, output_file)
    print(f"cleaned file saved to {output_file}")
