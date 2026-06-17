from app.config import Config


def test_config_uses_csv_data_directories():
    config = Config()
    assert config.RAW_DATA_DIR.replace("\\", "/").endswith("data/raw")
    assert config.CLEAN_DATA_DIR.replace("\\", "/").endswith("data/clean")
    assert config.CLEAN_DATA_FILE == ""


def test_config_reads_clean_data_file_from_environment(monkeypatch):
    monkeypatch.setenv("CLEAN_DATA_FILE", "data/clean/weather_clean_demo.csv")

    config = Config()

    assert config.CLEAN_DATA_FILE == "data/clean/weather_clean_demo.csv"
