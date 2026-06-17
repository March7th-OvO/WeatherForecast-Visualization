from collections import Counter, defaultdict
from datetime import date, datetime


def build_overview(rows: list[dict]) -> dict:
    if not rows:
        return {
            "total_records": 0,
            "total_cities": 0,
            "highest_temp": 0,
            "lowest_temp": 0,
        }

    return {
        "total_records": len(rows),
        "total_cities": len({row["city_name"] for row in rows}),
        "highest_temp": max(row["high_temp"] for row in rows),
        "lowest_temp": min(row["low_temp"] for row in rows),
    }


def build_weather_type_distribution(rows: list[dict]) -> list[dict]:
    counter = Counter(row["weather_type"] for row in rows)
    return [
        {"weather_type": weather_type, "count": count}
        for weather_type, count in counter.items()
    ]


def build_temperature_trend(rows: list[dict], limit: int = 30) -> list[dict]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[_normalize_date(row["weather_date"])].append(row["high_temp"])

    trend = []
    for weather_date in sorted(grouped.keys())[-limit:]:
        values = grouped[weather_date]
        trend.append(
            {
                "weather_date": weather_date.isoformat(),
                "avg_high_temp": round(sum(values) / len(values), 2),
            }
        )
    return trend


def build_city_average_temperatures(rows: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["city_name"]].append(row)

    averages = []
    for city_name, city_rows in grouped.items():
        averages.append(
            {
                "city_name": city_name,
                "avg_high_temp": round(
                    sum(row["high_temp"] for row in city_rows) / len(city_rows), 2
                ),
                "avg_low_temp": round(
                    sum(row["low_temp"] for row in city_rows) / len(city_rows), 2
                ),
            }
        )
    return averages


def build_province_average_temperatures(
    rows: list[dict], city_to_province: dict[str, str]
) -> list[dict]:
    grouped = defaultdict(list)
    for row in rows:
        province_name = city_to_province.get(row["city_name"])
        if province_name:
            grouped[province_name].append(row["high_temp"])

    return [
        {
            "province_name": province_name,
            "avg_high_temp": round(sum(values) / len(values), 2),
        }
        for province_name, values in grouped.items()
    ]


def _normalize_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()
