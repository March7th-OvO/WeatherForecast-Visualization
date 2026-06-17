import argparse
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
    parser = argparse.ArgumentParser(description="清洗原始天气 CSV")
    parser.add_argument("--input", type=str, default="", help="待清洗的原始 CSV 路径")
    parser.add_argument("--output", type=str, default="", help="清洗后 CSV 输出路径")
    args = parser.parse_args()

    latest_file = Path(args.input) if args.input else sorted(RAW_DIR.glob("weather_raw_*.csv"))[-1]
    output_file = (
        Path(args.output)
        if args.output
        else CLEAN_DIR / latest_file.name.replace("raw", "clean")
    )
    clean_csv(latest_file, output_file)
    print(f"cleaned file saved to {output_file}")
