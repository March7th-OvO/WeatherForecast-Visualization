"""
测试 db 模块 —— CSV 数据读取与类型转换。

验证 fetch_all_weather_rows() 能够：
1. 从 CSV 文件读取数据
2. 正确进行类型转换（字符串 → int）
3. 按日期降序排列结果
"""

from pathlib import Path

from app import create_app
from app.db import fetch_all_weather_rows


def test_fetch_all_weather_rows_reads_clean_csv(tmp_path):
    """
    验证从 CSV 读取天气数据的完整流程。

    使用 pytest 内置的 tmp_path fixture 创建临时文件，
    测试结束后自动清理，不留痕迹。

    关键验证点：
    - 温度从字符串转为 int 类型 (high_temp: 31 而非 "31")
    - 结果按 weather_date 降序排列（上海 06-18 排在 北京 06-17 前）
    - 需要 Flask app_context 以读取 app.config 中的配置
    """
    csv_path = tmp_path / "weather_clean_sample.csv"
    csv_path.write_text(
        "city_name,weather_date,weather_type,high_temp,low_temp,wind_level\n"
        "北京,2026-06-17,晴,31,21,<3级\n"
        "上海,2026-06-18,多云,29,23,<3级\n",
        encoding="utf-8-sig",
    )

    app = create_app()
    # 手动指定 CSV 路径，跳过自动查找逻辑
    app.config["CLEAN_DATA_FILE"] = str(csv_path)

    # Flask 的 app_context() 提供 current_app 和 g 等上下文变量
    with app.app_context():
        rows = fetch_all_weather_rows()

    # 验证：降序排列 + 类型转换
    assert rows == [
        {
            "city_name": "上海",
            "weather_date": "2026-06-18",
            "weather_type": "多云",
            "high_temp": 29,
            "low_temp": 23,
            "wind_level": "<3级",
        },
        {
            "city_name": "北京",
            "weather_date": "2026-06-17",
            "weather_type": "晴",
            "high_temp": 31,
            "low_temp": 21,
            "wind_level": "<3级",
        },
    ]
