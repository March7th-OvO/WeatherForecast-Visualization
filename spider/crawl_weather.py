"""
天气数据采集主控脚本。

将"城市列表加载 → 逐城抓取 → 结果汇总 → 写入 CSV"串联为一个完整的采集流程。

用法：
    # 抓取 100 个城市（默认）
    python -m spider.crawl_weather

    # 抓取 1400 个城市/站点（约 2 万条数据）
    python -m spider.crawl_weather --max-cities 1400
"""

import argparse
import csv
from datetime import datetime
from pathlib import Path

from spider.city_list import load_city_codes
from spider.weather_client import fetch_weather_html, parse_weather_rows


# 原始数据输出目录
RAW_DIR = Path("data/raw")

# CSV 表头字段定义（与数据库字段一致）
FIELDNAMES = [
    "city_name",      # 城市名
    "weather_date",   # 天气日期
    "weather_type",   # 天气状况（晴、阴、小雨等）
    "high_temp",      # 最高温
    "low_temp",       # 最低温
    "wind_level",     # 风力等级
]


def write_rows(rows: list[dict], output_path: Path) -> None:
    """
    将天气记录列表写入 CSV 文件。

    使用 csv.DictWriter：
    - 自动根据 FIELDNAMES 匹配字典键
    - utf-8-sig 编码兼容 Excel 直接打开
    - newline="" 防止 Windows 下多余空行

    Args:
        rows:        天气记录列表
        output_path: 输出文件路径
    """
    with output_path.open("w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()  # 写入表头
        writer.writerows(rows)  # 批量写入所有行


def build_city_url(city_code: str) -> str:
    """
    根据城市编码拼接中国天气网 15 天预报页面 URL。

    Args:
        city_code: 9 位城市编码，如 101010100（北京）

    Returns:
        完整 URL，如 https://e.weather.com.cn/mweather15d/101010100.shtml
    """
    return f"https://e.weather.com.cn/mweather15d/{city_code}.shtml"


def crawl_all_cities(max_cities: int = 100) -> list[dict]:
    """
    批量抓取所有城市的天气数据。

    流程：
    1. 加载城市列表（最多 max_cities 个）
    2. 遍历每个城市：
       a. 拼接天气页面 URL
       b. 请求页面 HTML
       c. 解析 15 天天气记录
       d. 追加到总结果列表中

    注意事项：
    - 单个城市抓取失败不会中断整个任务（requests 异常会被 load_city_codes 降级处理）
    - 各城市之间顺序抓取（非并发），避免触发反爬

    Args:
        max_cities: 最大抓取城市数量

    Returns:
        所有城市的天气记录汇总列表
    """
    all_rows: list[dict] = []
    for city in load_city_codes(max_cities):
        # 1. 拼接该城市的 15 天天气页面 URL
        url = build_city_url(city["city_code"])
        # 2. 请求页面 HTML
        html = fetch_weather_html(url)
        # 3. 解析 HTML 提取天气数据并添加到总列表
        all_rows.extend(parse_weather_rows(city["city_name"], html))
    return all_rows


def main() -> None:
    """命令行入口：解析参数 → 抓取 → 写入 CSV"""
    parser = argparse.ArgumentParser(description="从中国天气网抓取 15 天天气数据")
    parser.add_argument(
        "--max-cities", type=int, default=100, help="最多抓取的城市/站点数量"
    )
    args = parser.parse_args()

    # 确保原始数据目录存在
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # 执行抓取
    rows = crawl_all_cities(args.max_cities)

    # 输出文件名带时间戳，便于区分不同批次
    # 例如：weather_raw_20260617_170452.csv
    output_path = RAW_DIR / f"weather_raw_{datetime.now():%Y%m%d_%H%M%S}.csv"
    write_rows(rows, output_path)
    print(f"saved {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
