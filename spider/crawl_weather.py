import csv
from datetime import datetime
from pathlib import Path

from spider.city_list import CITY_NAMES
from spider.weather_client import fetch_weather_html, parse_weather_rows


RAW_DIR = Path("data/raw")
FIELDNAMES = [
    "city_name",
    "weather_date",
    "weather_type",
    "high_temp",
    "low_temp",
    "wind_level",
]


def write_rows(rows: list[dict], output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def build_city_url(city_name: str) -> str:
    return f"https://example.com/weather/{city_name}"


def crawl_all_cities() -> list[dict]:
    all_rows: list[dict] = []
    for city_name in CITY_NAMES:
        html = fetch_weather_html(build_city_url(city_name))
        all_rows.extend(parse_weather_rows(city_name, html))
    return all_rows


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    rows = crawl_all_cities()
    output_path = RAW_DIR / f"weather_raw_{datetime.now():%Y%m%d_%H%M%S}.csv"
    write_rows(rows, output_path)
    print(f"saved {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
