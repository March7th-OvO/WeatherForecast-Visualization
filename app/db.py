"""
数据访问层模块（纯 CSV 模式）。

当前项目不依赖 MySQL，直接从 CSV 文件读取清洗后的天气数据。
本模块负责：
1. 定位最新的清洗 CSV 文件
2. 使用 Pandas 读取并做类型转换（日期、温度转数值）
3. 将 DataFrame 转为字典列表，供 API 层使用
"""

from pathlib import Path

import pandas as pd
from flask import current_app


def fetch_all_weather_rows() -> list[dict]:
    """
    从清洗后的 CSV 文件中读取全部天气记录。

    处理流程：
    1. 解析 CSV 文件路径（手动指定或自动选最新）
    2. 用 Pandas 读取为 DataFrame
    3. 将 weather_date 转为日期类型，high_temp / low_temp 转为数值类型
    4. 剔除日期或温度字段为空的无效行
    5. 按日期降序排列，日期格式化为 YYYY-MM-DD 字符串，温度转为整数
    6. 返回核心 6 字段的字典列表

    Returns:
        list[dict]: 每项包含 city_name, weather_date, weather_type,
                    high_temp, low_temp, wind_level
    """
    csv_path = _resolve_clean_data_file()
    if not csv_path or not csv_path.exists():
        return []

    # 读取 CSV 为 DataFrame（Pandas 表格数据结构）
    frame = pd.read_csv(csv_path)
    if frame.empty:
        return []

    # ---- 类型转换与数据清洗 ----
    # 日期列：转为统一的 datetime 类型，无法解析的标记为 NaT
    frame["weather_date"] = pd.to_datetime(frame["weather_date"], errors="coerce")
    # 温度列：转为数值类型，无法解析的标记为 NaN
    frame["high_temp"] = pd.to_numeric(frame["high_temp"], errors="coerce")
    frame["low_temp"] = pd.to_numeric(frame["low_temp"], errors="coerce")
    # 剔除关键字段缺失的行
    frame = frame.dropna(subset=["weather_date", "high_temp", "low_temp"])

    # 按日期降序排列（最新的在前）
    frame = frame.sort_values("weather_date", ascending=False)

    # 格式化输出：日期 → YYYY-MM-DD，温度 → 整数
    frame["weather_date"] = frame["weather_date"].dt.strftime("%Y-%m-%d")
    frame["high_temp"] = frame["high_temp"].astype(int)
    frame["low_temp"] = frame["low_temp"].astype(int)

    # 只返回前端需要的 6 个核心字段
    return frame[
        [
            "city_name",
            "weather_date",
            "weather_type",
            "high_temp",
            "low_temp",
            "wind_level",
        ]
    ].to_dict(orient="records")


def _resolve_clean_data_file() -> Path | None:
    """
    确定要读取的清洗 CSV 文件路径。

    优先级：
    1. 如果 app.config 中配置了 CLEAN_DATA_FILE，直接使用该路径
    2. 否则在 data/clean/ 目录下查找最新的 weather_clean_*.csv

    Returns:
        Path 对象，如果找不到任何 CSV 则返回 None
    """
    configured_path = current_app.config.get("CLEAN_DATA_FILE", "")
    if configured_path:
        return Path(configured_path)

    clean_dir = Path(current_app.config["CLEAN_DATA_DIR"])
    # 按文件名排序（时间戳保证字母序 = 时间序），取最后一个即为最新
    csv_files = sorted(clean_dir.glob("weather_clean_*.csv"))
    if not csv_files:
        return None
    return csv_files[-1]
