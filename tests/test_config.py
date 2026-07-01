"""
测试 config 模块 —— 应用配置加载。

验证 Config 类能从环境变量和默认值中正确读取各项配置。
"""

from app.config import Config


def test_config_uses_data_directories_and_mysql_defaults(monkeypatch):
    """
    验证数据目录默认值。

    RAW_DATA_DIR 和 CLEAN_DATA_DIR 应正确指向项目根目录下的 data/ 子目录。
    """
    # 隔离本地 .env 或系统环境变量，确保这里验证的是代码默认值。
    for key in [
        "MYSQL_HOST",
        "MYSQL_PORT",
        "MYSQL_USER",
        "MYSQL_PASSWORD",
        "MYSQL_DATABASE",
    ]:
        monkeypatch.delenv(key, raising=False)

    config = Config()
    # 路径可能包含 Windows 反斜杠，统一转为 / 比较
    assert config.RAW_DATA_DIR.replace("\\", "/").endswith("data/raw")
    assert config.CLEAN_DATA_DIR.replace("\\", "/").endswith("data/clean")
    # 未配置 .env 时使用本地 MySQL 默认连接参数
    assert config.MYSQL_HOST == "127.0.0.1"
    assert config.MYSQL_PORT == 3306
    assert config.MYSQL_USER == "root"
    assert config.MYSQL_PASSWORD == "123456"
    assert config.MYSQL_DATABASE == "weather_visualization"


def test_config_reads_mysql_settings_from_environment(monkeypatch):
    """
    验证手动指定 MySQL 环境变量时能正确读取。

    使用 pytest 的 monkeypatch 临时设置环境变量，
    测试结束后自动恢复，不影响其他测试。
    """
    monkeypatch.setenv("MYSQL_HOST", "192.168.1.10")
    monkeypatch.setenv("MYSQL_PORT", "3306")
    monkeypatch.setenv("MYSQL_USER", "root")
    monkeypatch.setenv("MYSQL_PASSWORD", "123456")
    monkeypatch.setenv("MYSQL_DATABASE", "weather_test")

    config = Config()

    assert config.MYSQL_HOST == "192.168.1.10"
    assert config.MYSQL_PORT == 3306
    assert config.MYSQL_USER == "root"
    assert config.MYSQL_PASSWORD == "123456"
    assert config.MYSQL_DATABASE == "weather_test"
