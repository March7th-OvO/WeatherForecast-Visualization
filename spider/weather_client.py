from datetime import date

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0 WeatherVisualization/1.0",
}


def fetch_weather_html(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    response.encoding = "utf-8"
    return response.text


def parse_weather_rows(city_name: str, html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")

    mobile_rows = soup.select("li.h15li")
    if mobile_rows:
        return _parse_mobile_15d_rows(city_name, mobile_rows)

    table_rows = []
    for tr in soup.select("tr")[1:]:
        columns = [td.get_text(strip=True) for td in tr.select("td")]
        if len(columns) < 4:
            continue

        table_rows.append(
            {
                "city_name": city_name,
                "weather_date": columns[0],
                "weather_type": columns[1].split("/")[0],
                "high_temp": columns[2].replace("℃", "").split("/")[0],
                "low_temp": columns[2].replace("℃", "").split("/")[1],
                "wind_level": columns[3].split()[-1],
            }
        )

    return table_rows


def _parse_mobile_15d_rows(city_name: str, nodes) -> list[dict]:
    today = date.today()
    rows = []

    for node in nodes:
        date_label = node.select_one("p.h15listdayp2")
        weather_labels = node.select("div.h15k p")
        temp_label = node.select_one("div.h15listtem")
        wind_cells = node.select("div.h15xqobs td div")

        if not date_label or not weather_labels or not temp_label:
            continue

        month_text, day_text = date_label.get_text(strip=True).split("/")
        month_value = int(month_text)
        year_value = today.year + 1 if today.month == 12 and month_value == 1 else today.year
        weather_date = f"{year_value}-{month_value:02d}-{int(day_text):02d}"

        temperature_text = temp_label.get_text(strip=True).replace("℃", "")
        high_temp, low_temp = temperature_text.split("/")
        wind_text = wind_cells[0].get_text(strip=True) if wind_cells else ""

        rows.append(
            {
                "city_name": city_name,
                "weather_date": weather_date,
                "weather_type": weather_labels[-1].get_text(strip=True),
                "high_temp": high_temp,
                "low_temp": low_temp,
                "wind_level": wind_text,
            }
        )

    return rows
