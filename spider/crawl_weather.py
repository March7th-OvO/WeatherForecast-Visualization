import argparse
import csv
from datetime import datetime
from pathlib import Path

from spider.city_list import load_city_codes
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


def build_city_url(city_code: str) -> str:
    return f"https://e.weather.com.cn/mweather15d/{city_code}.shtml"


def crawl_all_cities(max_cities: int = 100) -> list[dict]:
    all_rows: list[dict] = []
    for city in load_city_codes(max_cities):
        html = fetch_weather_html(build_city_url(city["city_code"]))
        all_rows.extend(parse_weather_rows(city["city_name"], html))
    return all_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="从中国天气网抓取 15 天天气数据")
    parser.add_argument("--max-cities", type=int, default=100, help="最多抓取的城市/站点数量")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    rows = crawl_all_cities(args.max_cities)
    output_path = RAW_DIR / f"weather_raw_{datetime.now():%Y%m%d_%H%M%S}.csv"
    write_rows(rows, output_path)
    print(f"saved {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
