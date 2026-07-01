"""
天气页面抓取与 HTML 解析模块。

负责：
1. 通过 HTTP 请求中国天气网 15 天预报页面
2. 解析返回的 HTML（支持桌面版表格和移动版两种格式）
3. 提取每个城市的每日天气信息

中国天气网 15 天预报 URL 格式：
    https://e.weather.com.cn/mweather15d/{city_code}.shtml
"""

from datetime import date

import requests
from bs4 import BeautifulSoup


# 统一请求头，模拟正常浏览器访问
HEADERS = {
    "User-Agent": "Mozilla/5.0 WeatherVisualization/1.0",
}


def fetch_weather_html(url: str) -> str:
    """
    请求天气页面并返回 HTML 文本。

    Args:
        url: 中国天气网 15 天预报页面完整 URL

    Returns:
        页面 HTML 源代码字符串

    Raises:
        requests.HTTPError: 服务器返回非 2xx 状态码时抛出
    """
    response = requests.get(url, headers=HEADERS, timeout=20)
    # 检查 HTTP 状态码，非 2xx 抛出 HTTPError
    response.raise_for_status()
    # 强制 UTF-8 编码，避免中文乱码
    response.encoding = "utf-8"
    return response.text


def parse_weather_rows(city_name: str, html: str) -> list[dict]:
    """
    解析天气页面 HTML，提取 15 天天气数据。

    解析策略（自动适配两种页面格式）：
    1. 如果页面包含移动版元素 (li.h15li) → 走移动版解析
    2. 否则走桌面版 <table> 解析

    Args:
        city_name: 城市名（用于填充每条结果的 city_name 字段）
        html:      页面 HTML 源代码

    Returns:
        天气记录列表，每条包含 6 个字段：
        city_name, weather_date, weather_type, high_temp, low_temp, wind_level
    """
    soup = BeautifulSoup(html, "html.parser")

    # 中国天气网 15 天页面的移动版使用 li.h15li 作为每一天的容器
    mobile_rows = soup.select("li.h15li")
    if mobile_rows:
        return _parse_mobile_15d_rows(city_name, mobile_rows)

    # ---- 桌面版备用解析（基于 <table> 结构） ----
    table_rows = []
    # 跳过第一行 <tr>（表头），从第二行开始解析数据行
    for tr in soup.select("tr")[1:]:
        columns = [td.get_text(strip=True) for td in tr.select("td")]
        # 至少需要 4 列数据：日期、天气、气温、风力
        if len(columns) < 4:
            continue

        table_rows.append(
            {
                "city_name": city_name,
                "weather_date": columns[0],
                # 天气类型列可能包含 "晴/阴" 格式，取前半部分
                "weather_type": columns[1].split("/")[0],
                # 气温列格式 "12℃/5℃"，去除 ℃ 后拆分
                "high_temp": columns[2].replace("℃", "").split("/")[0],
                "low_temp": columns[2].replace("℃", "").split("/")[1],
                # 风力列格式 "北风 3-4级"，取最后一段
                "wind_level": columns[3].split()[-1],
            }
        )

    return table_rows


def _parse_mobile_15d_rows(city_name: str, nodes) -> list[dict]:
    """
    解析中国天气网移动版 15 天预报页面。

    移动版页面结构（每个 li.h15li 代表一天）：
    ┌──────────────────────────┐
    │ p.h15listdayp2 → "06/17" │  ← 月/日
    │ div.h15k p     → 天气描述 │  ← 取最后一个 p
    │ div.h15listtem → "35℃/22℃"│  ← 高温/低温
    │ div.h15xqobs   → 风力信息 │  ← td div
    └──────────────────────────┘

    Args:
        city_name: 城市名
        nodes:     BeautifulSoup 选中的 li.h15li 节点列表

    Returns:
        天气记录列表
    """
    today = date.today()
    rows = []

    for node in nodes:
        # ---- 提取各字段对应的 DOM 节点 ----
        date_label = node.select_one("p.h15listdayp2")       # 日期标签
        weather_labels = node.select("div.h15k p")            # 天气描述段落
        temp_label = node.select_one("div.h15listtem")        # 温度标签
        wind_cells = node.select("div.h15xqobs td div")       # 风力单元格

        # 如果关键字段缺失，跳过该天
        if not date_label or not weather_labels or not temp_label:
            continue

        # ---- 日期解析 ----
        # 移动版格式 "MM/DD"，需根据当前日期推断年份
        month_text, day_text = date_label.get_text(strip=True).split("/")
        month_value = int(month_text)
        # 跨年处理：如果现在是 12 月而预报是 1 月，说明是明年
        year_value = (
            today.year + 1 if today.month == 12 and month_value == 1 else today.year
        )
        weather_date = f"{year_value}-{month_value:02d}-{int(day_text):02d}"

        # ---- 温度解析 ----
        # 格式 "35℃/22℃" → ("35", "22")
        temperature_text = temp_label.get_text(strip=True).replace("℃", "")
        high_temp, low_temp = temperature_text.split("/")

        # ---- 天气类型 ----
        # 移动版天气描述可能有多行，取最后一个（通常是综合描述）
        # ---- 风力 ----
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
