"""
测试 config 模块 —— 应用配置加载。

验证 Config 类能从环境变量和默认值中正确读取各项配置。
"""

from app.config import Config


def test_config_uses_csv_data_directories():
    """
    验证数据目录默认值。

    RAW_DATA_DIR 和 CLEAN_DATA_DIR 应正确指向项目根目录下的 data/ 子目录。
    """
    config = Config()
    # 路径可能包含 Windows 反斜杠，统一转为 / 比较
    assert config.RAW_DATA_DIR.replace("\\", "/").endswith("data/raw")
    assert config.CLEAN_DATA_DIR.replace("\\", "/").endswith("data/clean")
    # 未配置 .env 时 CLEAN_DATA_FILE 默认为空字符串
    assert config.CLEAN_DATA_FILE == ""


def test_config_reads_clean_data_file_from_environment(monkeypatch):
    """
    验证手动指定 CLEAN_DATA_FILE 时能正确读取。

    使用 pytest 的 monkeypatch 临时设置环境变量，
    测试结束后自动恢复，不影响其他测试。
    """
    monkeypatch.setenv("CLEAN_DATA_FILE", "data/clean/weather_clean_demo.csv")

    config = Config()

    assert config.CLEAN_DATA_FILE == "data/clean/weather_clean_demo.csv"
