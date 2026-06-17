import json

import requests


DEFAULT_CITY_CODES = [
    {"city_name": "北京", "city_code": "101010100"},
    {"city_name": "上海", "city_code": "101020100"},
    {"city_name": "广州", "city_code": "101280101"},
    {"city_name": "深圳", "city_code": "101280601"},
    {"city_name": "成都", "city_code": "101270101"},
    {"city_name": "杭州", "city_code": "101210101"},
    {"city_name": "武汉", "city_code": "101200101"},
    {"city_name": "南京", "city_code": "101190101"},
    {"city_name": "西安", "city_code": "101110101"},
    {"city_name": "重庆", "city_code": "101040100"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 WeatherVisualization/1.0",
}


def load_city_codes(limit: int = 100) -> list[dict]:
    try:
        return _load_city_codes_from_weather(limit)
    except requests.RequestException:
        return DEFAULT_CITY_CODES[:limit]


def _load_city_codes_from_weather(limit: int) -> list[dict]:
    provinces = _load_json("https://www.weather.com.cn/data/city3jdata/china.html")
    cities: list[dict] = []

    for province_code in provinces.keys():
        province_cities = _load_json(
            f"https://www.weather.com.cn/data/city3jdata/provshi/{province_code}.html"
        )

        for city_suffix in province_cities.keys():
            city_prefix = f"{province_code}{city_suffix}"
            stations = _load_json(
                f"https://www.weather.com.cn/data/city3jdata/station/{city_prefix}.html"
            )

            for station_suffix, station_name in stations.items():
                if city_suffix == "00":
                    station_code = f"{province_code}{station_suffix}00"
                else:
                    station_code = f"{city_prefix}{station_suffix}"

                cities.append(
                    {
                        "city_name": station_name,
                        "city_code": station_code,
                    }
                )
                if len(cities) >= limit:
                    return cities

    return cities


def _load_json(url: str) -> dict:
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    response.encoding = "utf-8"
    return json.loads(response.text)
