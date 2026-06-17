from urllib.parse import unquote

from flask import Blueprint, jsonify, request

from app.db import fetch_all_weather_rows
from app.services.metrics import (
    build_city_average_temperatures,
    build_overview,
    build_province_average_temperatures,
    build_temperature_trend,
    build_weather_type_distribution,
)
from spider.city_list import load_city_codes


api_bp = Blueprint("api", __name__, url_prefix="/api")


def fetch_dashboard_payload():
    rows = fetch_all_weather_rows()
    if not rows:
        return {
            "overview": {
                "total_records": 0,
                "total_cities": 0,
                "highest_temp": 0,
                "lowest_temp": 0,
            },
            "trend": [],
            "weather_types": [],
        }

    return {
        "overview": build_overview(rows),
        "trend": build_temperature_trend(rows),
        "weather_types": build_weather_type_distribution(rows),
    }


def fetch_history_payload(city_name: str):
    rows = fetch_all_weather_rows()
    normalized_city_name = unquote(str(city_name)).strip()
    matched_rows = [
        _serialize_weather_row(row)
        for row in rows
        if str(row["city_name"]).strip() == normalized_city_name
    ]
    if matched_rows:
        return matched_rows

    if not rows:
        return []

    fallback_city_name = str(rows[0]["city_name"]).strip()
    return [
        _serialize_weather_row(row)
        for row in rows
        if str(row["city_name"]).strip() == fallback_city_name
    ]


@api_bp.get("/dashboard")
def dashboard_data():
    return jsonify(fetch_dashboard_payload())


@api_bp.get("/map")
def map_data():
    rows = fetch_all_weather_rows()
    city_metadata = load_city_codes(2000)
    city_to_province = {
        item["city_name"]: item["province_name"] for item in city_metadata if item.get("province_name")
    }
    return jsonify({"provinces": build_province_average_temperatures(rows, city_to_province)})


@api_bp.get("/analysis")
def analysis_data():
    rows = fetch_all_weather_rows()
    city_averages = build_city_average_temperatures(rows)
    high_top10 = sorted(
        city_averages,
        key=lambda item: item["avg_high_temp"],
        reverse=True,
    )[:10]
    low_top10 = sorted(city_averages, key=lambda item: item["avg_low_temp"])[:10]

    return jsonify(
        {
            "high_top10": high_top10,
            "low_top10": low_top10,
            "weather_types": build_weather_type_distribution(rows),
        }
    )


@api_bp.get("/history")
def history_data():
    city_name = request.args.get("city_name", "北京")
    return jsonify(fetch_history_payload(city_name))


def _serialize_weather_row(row: dict) -> dict:
    serialized = dict(row)
    weather_date = serialized.get("weather_date")
    if hasattr(weather_date, "isoformat"):
        serialized["weather_date"] = weather_date.isoformat()
    return serialized
