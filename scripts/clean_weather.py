"""
天气数据清洗脚本。

将爬虫产出的原始 CSV 转化为结构统一的清洗 CSV，并默认持久化到 MySQL。

清洗规则：
1. 所有字符串字段去除首尾空格
2. 温度字段转为整数类型
3. 按 (城市名, 日期) 去重，保留首次出现的记录

用法：
    # 自动选择最新的原始 CSV 进行清洗
    python -m scripts.clean_weather

    # 手动指定输入输出文件
    python -m scripts.clean_weather --input data/raw/weather_raw_xxx.csv --output data/clean/weather_clean_xxx.csv

    # 只生成清洗 CSV，不导入 MySQL
    python -m scripts.clean_weather --skip-mysql
"""

import argparse
from pathlib import Path

import pandas as pd


# 数据目录常量
RAW_DIR = Path("data/raw")    # 原始爬虫数据
CLEAN_DIR = Path("data/clean")  # 清洗后数据


def normalize_row(row: dict) -> dict:
    """
    标准化单行记录。

    处理内容：
    - 字符串字段去除首尾多余空格
    - 高低温从字符串转为整数（如 "12" → 12）

    Args:
        row: 从原始 CSV 读取的一行（dict 格式）

    Returns:
        标准化后的字典，所有字段整洁可用
    """
    return {
        "city_name": row["city_name"].strip(),
        "weather_date": row["weather_date"].strip(),
        "weather_type": row["weather_type"].strip(),
        "high_temp": int(str(row["high_temp"]).strip()),
        "low_temp": int(str(row["low_temp"]).strip()),
        "wind_level": row["wind_level"].strip(),
    }


def clean_csv(input_path: Path, output_path: Path) -> None:
    """
    执行 CSV 清洗主流程。

    步骤：
    1. 用 Pandas 读取原始 CSV
    2. 逐行标准化
    3. 按 (city_name, weather_date) 去重
    4. 输出为 UTF-8 BOM 编码的 CSV（Excel 可直接打开不乱码）

    Args:
        input_path:  原始 CSV 文件路径
        output_path: 清洗后 CSV 输出路径
    """
    # 读取原始 CSV → DataFrame
    frame = pd.read_csv(input_path)

    # 逐行标准化清洗
    cleaned_rows = [normalize_row(row) for row in frame.to_dict(orient="records")]

    # 转回 DataFrame 并去重
    # subset 指定去重依据的列：同一城市同一天只保留一条
    cleaned_frame = pd.DataFrame(cleaned_rows).drop_duplicates(
        subset=["city_name", "weather_date"]
    )

    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # utf-8-sig 编码：文件头带 BOM 标记，Windows Excel 双击打开不乱码
    cleaned_frame.to_csv(output_path, index=False, encoding="utf-8-sig")


# =============================================================================
# 命令行入口
# =============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="清洗原始天气 CSV")
    parser.add_argument("--input", type=str, default="", help="待清洗的原始 CSV 路径")
    parser.add_argument("--output", type=str, default="", help="清洗后 CSV 输出路径")
    parser.add_argument(
        "--skip-mysql",
        action="store_true",
        help="只输出清洗 CSV，不将结果导入 MySQL",
    )
    args = parser.parse_args()

    # 自动选择最新的原始 CSV（按文件名排序取最后一个）
    latest_file = (
        Path(args.input)
        if args.input
        else sorted(RAW_DIR.glob("weather_raw_*.csv"))[-1]
    )

    # 输出文件名默认将 "raw" 替换为 "clean"
    output_file = (
        Path(args.output)
        if args.output
        else CLEAN_DIR / latest_file.name.replace("raw", "clean")
    )

    clean_csv(latest_file, output_file)
    print(f"cleaned file saved to {output_file}")

    if not args.skip_mysql:
        # 清洗后的 CSV 是导入源；页面渲染时 Flask API 会直接从 MySQL 读取数据。
        from scripts.import_weather import import_clean_csv_to_mysql, load_mysql_config

        imported = import_clean_csv_to_mysql(output_file, load_mysql_config())
        print(f"imported {imported} rows into MySQL from {output_file}")
