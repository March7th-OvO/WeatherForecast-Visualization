import os

from app.config import Config


def test_config_uses_sqlalchemy_style_mysql_uri_fields():
    config = Config()
    assert config.MYSQL_HOST == "127.0.0.1"
    assert config.MYSQL_PORT == 3306
    assert config.RAW_DATA_DIR.replace("\\", "/").endswith("data/raw")
    assert config.CLEAN_DATA_DIR.replace("\\", "/").endswith("data/clean")


def test_config_reads_mysql_values_from_environment(monkeypatch):
    monkeypatch.setenv("MYSQL_PORT", "3307")
    monkeypatch.setenv("MYSQL_USER", "weatherapp")

    config = Config()

    assert config.MYSQL_PORT == 3307
    assert config.MYSQL_USER == "weatherapp"
