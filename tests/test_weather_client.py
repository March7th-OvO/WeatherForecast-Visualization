from unittest.mock import Mock, patch

from spider.weather_client import fetch_weather_html, parse_weather_rows


HTML = """
<table>
  <tr><th>日期</th><th>天气现象</th><th>气温</th><th>风力风向</th></tr>
  <tr>
    <td>2026-01-01</td>
    <td>晴/阴</td>
    <td>10℃/-1℃</td>
    <td>北风 3-4级</td>
  </tr>
</table>
"""


def test_parse_weather_rows_returns_expected_fields():
    rows = parse_weather_rows("北京", HTML)
    assert rows == [
        {
            "city_name": "北京",
            "weather_date": "2026-01-01",
            "weather_type": "晴",
            "high_temp": "10",
            "low_temp": "-1",
            "wind_level": "3-4级",
        }
    ]


@patch("spider.weather_client.requests.get")
def test_fetch_weather_html_returns_text(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = "<html>ok</html>"
    mock_get.return_value = mock_response

    html = fetch_weather_html("https://example.com/weather")

    assert html == "<html>ok</html>"
