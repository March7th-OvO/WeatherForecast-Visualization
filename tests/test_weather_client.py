"""
测试 weather_client 模块 —— 天气页面抓取与 HTML 解析。

测试策略：
- 用 mock 替换 requests.get，避免真实网络请求
- 用一段静态 HTML 验证解析逻辑的正确性
"""

from unittest.mock import Mock, patch

from spider.weather_client import fetch_weather_html, parse_weather_rows


# 模拟的桌面版天气表格 HTML 片段
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
    """
    验证解析桌面版 HTML 表格的正确性。

    检查点：
    - 天气类型取 "/" 前半部分（"晴/阴" → "晴"）
    - 温度按 "/" 拆分并去除 ℃ 符号
    - 风力取最后一词（"北风 3-4级" → "3-4级"）
    """
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
    """
    验证 HTTP 请求函数的行为（使用 mock 网络）。

    @patch 装饰器将 requests.get 替换为 mock 对象，
    测试不会真正发送网络请求。
    """
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = "<html>ok</html>"
    mock_get.return_value = mock_response

    html = fetch_weather_html("https://example.com/weather")

    assert html == "<html>ok</html>"
