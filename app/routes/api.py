from flask import Blueprint, jsonify, request

from app.db import fetch_all_weather_rows
from app.services.metrics import (
    build_city_average_temperatures,
    build_overview,
    build_temperature_trend,
    build_weather_type_distribution,
)


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
    return [row for row in rows if row["city_name"] == city_name]


@api_bp.get("/dashboard")
def dashboard_data():
    return jsonify(fetch_dashboard_payload())


@api_bp.get("/map")
def map_data():
    rows = fetch_all_weather_rows()
    return jsonify({"cities": build_city_average_temperatures(rows)})


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
