import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0 WeatherVisualization/1.0",
}


def fetch_weather_html(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return response.text


def parse_weather_rows(city_name: str, html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    rows: list[dict] = []

    for tr in soup.select("tr")[1:]:
        columns = [td.get_text(strip=True) for td in tr.select("td")]
        if len(columns) < 4:
            continue

        date_text = columns[0]
        weather_text = columns[1].split("/")[0]
        temp_pair = columns[2].replace("℃", "").split("/")
        wind_text = columns[3].split()[-1]

        rows.append(
            {
                "city_name": city_name,
                "weather_date": date_text,
                "weather_type": weather_text,
                "high_temp": temp_pair[0],
                "low_temp": temp_pair[1],
                "wind_level": wind_text,
            }
        )

    return rows
