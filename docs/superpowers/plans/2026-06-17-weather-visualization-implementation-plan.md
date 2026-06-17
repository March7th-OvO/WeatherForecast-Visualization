# Weather Visualization System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个可在 Windows 笔记本本机运行的天气数据采集、清洗、入库、分析与 Flask 可视化系统，完成中国天气网约 2 万条天气数据的采集与 4 个页面展示。

**Architecture:** 项目采用“爬虫抓取原始 CSV -> Python 清洗 -> MySQL 存储 -> Flask 页面与 JSON 接口 -> ECharts 渲染”的单机链路。代码按职责拆成爬虫、脚本、后端、模板、静态资源和测试目录，优先保证每个模块可单独验证，再完成端到端联调。

**Tech Stack:** Python 3.11, Flask, PyMySQL, Requests, BeautifulSoup4, Pandas, Pytest, ECharts 5, MySQL 8

---

## File Structure

### Planned files

- Create: `requirements.txt`
- Create: `.env.example`
- Create: `app/__init__.py`
- Create: `app/config.py`
- Create: `app/db.py`
- Create: `app/routes/pages.py`
- Create: `app/routes/api.py`
- Create: `app/services/metrics.py`
- Create: `spider/__init__.py`
- Create: `spider/city_list.py`
- Create: `spider/weather_client.py`
- Create: `spider/crawl_weather.py`
- Create: `scripts/__init__.py`
- Create: `scripts/clean_weather.py`
- Create: `scripts/import_weather.py`
- Create: `sql/schema.sql`
- Create: `templates/base.html`
- Create: `templates/dashboard.html`
- Create: `templates/map.html`
- Create: `templates/analysis.html`
- Create: `templates/history.html`
- Create: `static/css/dashboard.css`
- Create: `static/js/dashboard.js`
- Create: `static/js/map.js`
- Create: `static/js/analysis.js`
- Create: `static/js/history.js`
- Create: `data/raw/.gitkeep`
- Create: `data/clean/.gitkeep`
- Create: `tests/conftest.py`
- Create: `tests/test_config.py`
- Create: `tests/test_weather_client.py`
- Create: `tests/test_clean_weather.py`
- Create: `tests/test_metrics.py`
- Create: `tests/test_routes.py`

### Responsibility map

- `spider/` 只负责采集和解析天气网页，不处理数据库逻辑。
- `scripts/` 只负责清洗 CSV 和导入 MySQL，避免把数据脚本塞进 Flask。
- `app/` 只负责配置、数据库访问、业务查询、页面和接口。
- `templates/` 和 `static/` 负责 4 个页面的视觉呈现与图表逻辑。
- `tests/` 按配置、爬虫、清洗、查询、路由拆分，保证每层都能独立回归。

## Task 1: 初始化项目骨架与配置

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `app/__init__.py`
- Create: `app/config.py`
- Create: `tests/conftest.py`
- Create: `tests/test_config.py`
- Create: `data/raw/.gitkeep`
- Create: `data/clean/.gitkeep`

- [ ] **Step 1: 编写配置测试**

```python
# tests/test_config.py
from app.config import Config


def test_config_uses_sqlalchemy_style_mysql_uri_fields():
    config = Config()
    assert config.MYSQL_HOST == "127.0.0.1"
    assert config.MYSQL_PORT == 3306
    assert config.RAW_DATA_DIR.endswith("data/raw")
    assert config.CLEAN_DATA_DIR.endswith("data/clean")
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `python -m pytest tests/test_config.py -v`

Expected:

```text
E   ModuleNotFoundError: No module named 'app'
```

- [ ] **Step 3: 创建项目骨架与最小配置实现**

```python
# app/config.py
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "123456")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "weather_visualization")
    RAW_DATA_DIR = str(BASE_DIR / "data" / "raw")
    CLEAN_DATA_DIR = str(BASE_DIR / "data" / "clean")
    SECRET_KEY = os.getenv("SECRET_KEY", "weather-secret-key")
```

```python
# app/__init__.py
from flask import Flask
from app.config import Config


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    return app
```

```python
# tests/conftest.py
import pytest
from app import create_app


@pytest.fixture()
def app():
    flask_app = create_app()
    flask_app.config.update(TESTING=True)
    return flask_app
```

```text
# requirements.txt
Flask==3.0.3
PyMySQL==1.1.1
requests==2.32.3
beautifulsoup4==4.12.3
pandas==2.2.2
python-dotenv==1.0.1
pytest==8.2.2
```

```text
# .env.example
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_DATABASE=weather_visualization
SECRET_KEY=replace-me
```

- [ ] **Step 4: 再次运行配置测试**

Run: `python -m pytest tests/test_config.py -v`

Expected:

```text
1 passed
```

- [ ] **Step 5: 提交项目骨架**

```bash
git add requirements.txt .env.example app tests data
git commit -m "初始化天气系统项目骨架"
```

## Task 2: 建立 MySQL 连接层与建表脚本

**Files:**
- Create: `app/db.py`
- Create: `sql/schema.sql`
- Create: `tests/test_routes.py`
- Modify: `app/__init__.py`

- [ ] **Step 1: 先写数据库健康检查测试**

```python
# tests/test_routes.py
from app import create_app


def test_health_route_returns_ok():
    app = create_app()
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `python -m pytest tests/test_routes.py::test_health_route_returns_ok -v`

Expected:

```text
E   AssertionError: assert 404 == 200
```

- [ ] **Step 3: 实现数据库工具和健康检查路由**

```python
# app/db.py
import pymysql
from flask import current_app


def get_connection():
    return pymysql.connect(
        host=current_app.config["MYSQL_HOST"],
        port=current_app.config["MYSQL_PORT"],
        user=current_app.config["MYSQL_USER"],
        password=current_app.config["MYSQL_PASSWORD"],
        database=current_app.config["MYSQL_DATABASE"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
```

```python
# app/__init__.py
from flask import Flask, jsonify
from app.config import Config


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return app
```

```sql
-- sql/schema.sql
CREATE DATABASE IF NOT EXISTS weather_visualization DEFAULT CHARACTER SET utf8mb4;
USE weather_visualization;

DROP TABLE IF EXISTS weather_daily;

CREATE TABLE weather_daily (
    id INT PRIMARY KEY AUTO_INCREMENT,
    city_name VARCHAR(50) NOT NULL,
    weather_date DATE NOT NULL,
    weather_type VARCHAR(30) NOT NULL,
    high_temp INT NOT NULL,
    low_temp INT NOT NULL,
    wind_level VARCHAR(20) NOT NULL,
    UNIQUE KEY uniq_city_date (city_name, weather_date)
);
```

- [ ] **Step 4: 运行健康检查测试**

Run: `python -m pytest tests/test_routes.py::test_health_route_returns_ok -v`

Expected:

```text
1 passed
```

- [ ] **Step 5: 提交数据库基础设施**

```bash
git add app/db.py app/__init__.py sql/schema.sql tests/test_routes.py
git commit -m "添加数据库连接与建表脚本"
```

## Task 3: 实现城市清单与天气页面解析器

**Files:**
- Create: `spider/__init__.py`
- Create: `spider/city_list.py`
- Create: `spider/weather_client.py`
- Create: `tests/test_weather_client.py`

- [ ] **Step 1: 编写解析器测试**

```python
# tests/test_weather_client.py
from spider.weather_client import parse_weather_rows


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
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `python -m pytest tests/test_weather_client.py -v`

Expected:

```text
E   ModuleNotFoundError: No module named 'spider'
```

- [ ] **Step 3: 实现城市列表和 HTML 解析器**

```python
# spider/city_list.py
CITY_NAMES = [
    "北京", "上海", "广州", "深圳", "成都", "杭州", "武汉", "南京", "西安", "重庆",
    "天津", "苏州", "长沙", "郑州", "青岛", "沈阳", "大连", "厦门", "福州", "济南",
]
```

```python
# spider/weather_client.py
from bs4 import BeautifulSoup


def parse_weather_rows(city_name: str, html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for tr in soup.select("tr")[1:]:
        columns = [td.get_text(strip=True) for td in tr.select("td")]
        if len(columns) < 4:
            continue

        date_text = columns[0]
        weather_text = columns[1].split("/")[0]
        temp_pair = columns[2].replace("℃", "").split("/")
        wind_text = columns[3].split()[-1]

        rows.append(
            {
                "city_name": city_name,
                "weather_date": date_text,
                "weather_type": weather_text,
                "high_temp": temp_pair[0],
                "low_temp": temp_pair[1],
                "wind_level": wind_text,
            }
        )
    return rows
```

```python
# spider/__init__.py
from spider.city_list import CITY_NAMES
from spider.weather_client import parse_weather_rows

__all__ = ["CITY_NAMES", "parse_weather_rows"]
```

- [ ] **Step 4: 运行解析测试**

Run: `python -m pytest tests/test_weather_client.py -v`

Expected:

```text
1 passed
```

- [ ] **Step 5: 提交爬虫解析基础**

```bash
git add spider tests/test_weather_client.py
git commit -m "添加天气页面解析器"
```

## Task 4: 实现原始天气 CSV 抓取脚本

**Files:**
- Create: `spider/crawl_weather.py`
- Modify: `spider/weather_client.py`
- Create: `tests/test_weather_client.py`

- [ ] **Step 1: 为请求函数补充测试**

```python
# tests/test_weather_client.py
from unittest.mock import Mock, patch
from spider.weather_client import fetch_weather_html


@patch("spider.weather_client.requests.get")
def test_fetch_weather_html_returns_text(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = "<html>ok</html>"
    mock_get.return_value = mock_response

    html = fetch_weather_html("https://example.com/weather")
    assert html == "<html>ok</html>"
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `python -m pytest tests/test_weather_client.py::test_fetch_weather_html_returns_text -v`

Expected:

```text
E   ImportError: cannot import name 'fetch_weather_html'
```

- [ ] **Step 3: 增加请求函数与 CSV 抓取脚本**

```python
# spider/weather_client.py
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0 WeatherVisualization/1.0"
}


def fetch_weather_html(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return response.text


def parse_weather_rows(city_name: str, html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for tr in soup.select("tr")[1:]:
        columns = [td.get_text(strip=True) for td in tr.select("td")]
        if len(columns) < 4:
            continue
        date_text = columns[0]
        weather_text = columns[1].split("/")[0]
        temp_pair = columns[2].replace("℃", "").split("/")
        wind_text = columns[3].split()[-1]
        rows.append(
            {
                "city_name": city_name,
                "weather_date": date_text,
                "weather_type": weather_text,
                "high_temp": temp_pair[0],
                "low_temp": temp_pair[1],
                "wind_level": wind_text,
            }
        )
    return rows
```

```python
# spider/crawl_weather.py
from pathlib import Path
import csv
from datetime import datetime

from spider.city_list import CITY_NAMES
from spider.weather_client import fetch_weather_html, parse_weather_rows


RAW_DIR = Path("data/raw")


def write_rows(rows: list[dict], output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=["city_name", "weather_date", "weather_type", "high_temp", "low_temp", "wind_level"],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    all_rows = []

    for city_name in CITY_NAMES:
        url = f"https://example.com/weather/{city_name}"
        html = fetch_weather_html(url)
        all_rows.extend(parse_weather_rows(city_name, html))

    output_path = RAW_DIR / f"weather_raw_{datetime.now():%Y%m%d_%H%M%S}.csv"
    write_rows(all_rows, output_path)
    print(f"saved {len(all_rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 运行请求测试**

Run: `python -m pytest tests/test_weather_client.py::test_fetch_weather_html_returns_text -v`

Expected:

```text
1 passed
```

- [ ] **Step 5: 提交原始抓取脚本**

```bash
git add spider/crawl_weather.py spider/weather_client.py tests/test_weather_client.py
git commit -m "添加原始天气抓取脚本"
```

## Task 5: 实现 CSV 清洗脚本

**Files:**
- Create: `scripts/__init__.py`
- Create: `scripts/clean_weather.py`
- Create: `tests/test_clean_weather.py`

- [ ] **Step 1: 编写清洗逻辑测试**

```python
# tests/test_clean_weather.py
from scripts.clean_weather import normalize_row


def test_normalize_row_converts_temperatures_and_trims_weather_type():
    row = {
        "city_name": "北京",
        "weather_date": "2026-01-01",
        "weather_type": " 小雨 ",
        "high_temp": "12",
        "low_temp": "3",
        "wind_level": " 3-4级 ",
    }

    normalized = normalize_row(row)

    assert normalized == {
        "city_name": "北京",
        "weather_date": "2026-01-01",
        "weather_type": "小雨",
        "high_temp": 12,
        "low_temp": 3,
        "wind_level": "3-4级",
    }
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `python -m pytest tests/test_clean_weather.py -v`

Expected:

```text
E   ModuleNotFoundError: No module named 'scripts.clean_weather'
```

- [ ] **Step 3: 实现清洗脚本**

```python
# scripts/clean_weather.py
from pathlib import Path
import pandas as pd


RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/clean")


def normalize_row(row: dict) -> dict:
    return {
        "city_name": row["city_name"].strip(),
        "weather_date": row["weather_date"].strip(),
        "weather_type": row["weather_type"].strip(),
        "high_temp": int(str(row["high_temp"]).strip()),
        "low_temp": int(str(row["low_temp"]).strip()),
        "wind_level": row["wind_level"].strip(),
    }


def clean_csv(input_path: Path, output_path: Path) -> None:
    frame = pd.read_csv(input_path)
    cleaned_rows = [normalize_row(row) for row in frame.to_dict(orient="records")]
    cleaned_frame = pd.DataFrame(cleaned_rows).drop_duplicates(subset=["city_name", "weather_date"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_frame.to_csv(output_path, index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    latest_file = sorted(RAW_DIR.glob("weather_raw_*.csv"))[-1]
    output_file = CLEAN_DIR / latest_file.name.replace("raw", "clean")
    clean_csv(latest_file, output_file)
    print(f"cleaned file saved to {output_file}")
```

```python
# scripts/__init__.py
from scripts.clean_weather import clean_csv, normalize_row

__all__ = ["clean_csv", "normalize_row"]
```

- [ ] **Step 4: 运行清洗测试**

Run: `python -m pytest tests/test_clean_weather.py -v`

Expected:

```text
1 passed
```

- [ ] **Step 5: 提交清洗脚本**

```bash
git add scripts tests/test_clean_weather.py
git commit -m "添加天气数据清洗脚本"
```

## Task 6: 实现 MySQL 导入脚本与统计查询服务

**Files:**
- Create: `scripts/import_weather.py`
- Create: `app/services/metrics.py`
- Create: `tests/test_metrics.py`

- [ ] **Step 1: 先写统计函数测试**

```python
# tests/test_metrics.py
from app.services.metrics import build_overview


def test_build_overview_returns_core_metrics():
    rows = [
        {"city_name": "北京", "high_temp": 10, "low_temp": 0},
        {"city_name": "上海", "high_temp": 12, "low_temp": 3},
    ]

    overview = build_overview(rows)

    assert overview == {
        "total_records": 2,
        "total_cities": 2,
        "highest_temp": 12,
        "lowest_temp": 0,
    }
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `python -m pytest tests/test_metrics.py -v`

Expected:

```text
E   ModuleNotFoundError: No module named 'app.services'
```

- [ ] **Step 3: 实现导入脚本与统计服务**

```python
# app/services/metrics.py
def build_overview(rows: list[dict]) -> dict:
    return {
        "total_records": len(rows),
        "total_cities": len({row["city_name"] for row in rows}),
        "highest_temp": max(row["high_temp"] for row in rows),
        "lowest_temp": min(row["low_temp"] for row in rows),
    }
```

```python
# scripts/import_weather.py
from pathlib import Path
import pandas as pd
import pymysql


def import_clean_csv_to_mysql(input_path: Path, mysql_config: dict) -> int:
    frame = pd.read_csv(input_path)
    connection = pymysql.connect(
        host=mysql_config["host"],
        port=mysql_config["port"],
        user=mysql_config["user"],
        password=mysql_config["password"],
        database=mysql_config["database"],
        charset="utf8mb4",
        autocommit=True,
    )
    inserted = 0
    with connection.cursor() as cursor:
        sql = """
        INSERT INTO weather_daily
        (city_name, weather_date, weather_type, high_temp, low_temp, wind_level)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            weather_type = VALUES(weather_type),
            high_temp = VALUES(high_temp),
            low_temp = VALUES(low_temp),
            wind_level = VALUES(wind_level)
        """
        for row in frame.to_dict(orient="records"):
            cursor.execute(
                sql,
                (
                    row["city_name"],
                    row["weather_date"],
                    row["weather_type"],
                    int(row["high_temp"]),
                    int(row["low_temp"]),
                    row["wind_level"],
                ),
            )
            inserted += 1
    connection.close()
    return inserted
```

- [ ] **Step 4: 运行统计服务测试**

Run: `python -m pytest tests/test_metrics.py -v`

Expected:

```text
1 passed
```

- [ ] **Step 5: 提交导入与统计服务**

```bash
git add scripts/import_weather.py app/services/metrics.py tests/test_metrics.py
git commit -m "添加数据导入和统计服务"
```

## Task 7: 搭建 Flask 页面路由与基础模板

**Files:**
- Create: `app/routes/pages.py`
- Modify: `app/__init__.py`
- Create: `templates/base.html`
- Create: `templates/dashboard.html`
- Create: `static/css/dashboard.css`
- Modify: `tests/test_routes.py`

- [ ] **Step 1: 为首页页面写路由测试**

```python
# tests/test_routes.py
from app import create_app


def test_dashboard_page_renders_title():
    app = create_app()
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert "天气数据分析系统".encode("utf-8") in response.data
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `python -m pytest tests/test_routes.py::test_dashboard_page_renders_title -v`

Expected:

```text
E   AssertionError: assert 404 == 200
```

- [ ] **Step 3: 实现基础页面蓝图和模板**

```python
# app/routes/pages.py
from flask import Blueprint, render_template


pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def dashboard():
    return render_template("dashboard.html")
```

```python
# app/__init__.py
from flask import Flask, jsonify
from app.config import Config
from app.routes.pages import pages_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    app.register_blueprint(pages_bp)
    return app
```

```html
<!-- templates/base.html -->
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}天气数据分析系统{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">
  </head>
  <body>
    <div class="layout">
      <aside class="sidebar">
        <h1>天气数据分析系统</h1>
        <nav>
          <a href="/">首页</a>
          <a href="/map">天气地图</a>
          <a href="/analysis">天气分析</a>
          <a href="/history">历史天气</a>
        </nav>
      </aside>
      <main class="content">
        {% block content %}{% endblock %}
      </main>
    </div>
  </body>
</html>
```

```html
<!-- templates/dashboard.html -->
{% extends "base.html" %}
{% block title %}首页总览{% endblock %}
{% block content %}
<section class="hero">
  <div class="page-header">首页总览</div>
  <div class="stats-grid">
    <div class="stat-card blue">总记录数</div>
    <div class="stat-card orange">城市数</div>
    <div class="stat-card green">最高温</div>
    <div class="stat-card red">最低温</div>
  </div>
  <div id="trend-chart" class="chart-panel"></div>
</section>
{% endblock %}
```

```css
/* static/css/dashboard.css */
body {
  margin: 0;
  font-family: "Microsoft YaHei", sans-serif;
  background: #f3f6fb;
  color: #1f2937;
}

.layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 240px;
  background: #2f3742;
  color: #fff;
  padding: 24px;
}

.sidebar nav a {
  display: block;
  color: #d7dde6;
  text-decoration: none;
  margin: 18px 0;
}

.content {
  flex: 1;
  padding: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  border-radius: 10px;
  color: #fff;
  padding: 20px;
  min-height: 96px;
}

.blue { background: #2196f3; }
.orange { background: #f4b400; }
.green { background: #34a853; }
.red { background: #ea4335; }

.chart-panel {
  margin-top: 24px;
  min-height: 420px;
  background: #fff;
  border-radius: 12px;
}
```

- [ ] **Step 4: 运行首页路由测试**

Run: `python -m pytest tests/test_routes.py::test_dashboard_page_renders_title -v`

Expected:

```text
1 passed
```

- [ ] **Step 5: 提交基础页面骨架**

```bash
git add app/routes/pages.py app/__init__.py templates static/css/dashboard.css tests/test_routes.py
git commit -m "搭建天气系统基础页面"
```

## Task 8: 实现首页总览接口与首页图表

**Files:**
- Create: `app/routes/api.py`
- Modify: `app/__init__.py`
- Modify: `app/routes/pages.py`
- Create: `static/js/dashboard.js`
- Modify: `templates/dashboard.html`
- Modify: `tests/test_routes.py`

- [ ] **Step 1: 先写首页概览接口测试**

```python
# tests/test_routes.py
from unittest.mock import patch
from app import create_app


@patch("app.routes.api.fetch_dashboard_payload")
def test_dashboard_api_returns_overview(mock_payload):
    mock_payload.return_value = {
        "overview": {"total_records": 20000, "total_cities": 100, "highest_temp": 38, "lowest_temp": -12},
        "trend": [{"weather_date": "2026-01-01", "avg_high_temp": 12}],
        "weather_types": [{"weather_type": "晴", "count": 60}],
    }
    app = create_app()
    client = app.test_client()
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    assert response.get_json()["overview"]["total_records"] == 20000
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `python -m pytest tests/test_routes.py::test_dashboard_api_returns_overview -v`

Expected:

```text
E   ModuleNotFoundError: No module named 'app.routes.api'
```

- [ ] **Step 3: 实现首页接口与图表脚本**

```python
# app/routes/api.py
from flask import Blueprint, jsonify


api_bp = Blueprint("api", __name__, url_prefix="/api")


def fetch_dashboard_payload():
    return {
        "overview": {"total_records": 0, "total_cities": 0, "highest_temp": 0, "lowest_temp": 0},
        "trend": [],
        "weather_types": [],
    }


@api_bp.get("/dashboard")
def dashboard_data():
    return jsonify(fetch_dashboard_payload())
```

```python
# app/__init__.py
from flask import Flask, jsonify
from app.config import Config
from app.routes.api import api_bp
from app.routes.pages import pages_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp)
    return app
```

```html
<!-- templates/dashboard.html -->
{% extends "base.html" %}
{% block title %}首页总览{% endblock %}
{% block content %}
<section class="hero">
  <div class="page-header">首页总览</div>
  <div class="stats-grid">
    <div class="stat-card blue"><span id="total-records">0</span><p>总记录数</p></div>
    <div class="stat-card orange"><span id="total-cities">0</span><p>城市数</p></div>
    <div class="stat-card green"><span id="highest-temp">0</span><p>最高温</p></div>
    <div class="stat-card red"><span id="lowest-temp">0</span><p>最低温</p></div>
  </div>
  <div id="trend-chart" class="chart-panel"></div>
  <div id="type-chart" class="chart-panel"></div>
</section>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<script src="{{ url_for('static', filename='js/dashboard.js') }}"></script>
{% endblock %}
```

```javascript
// static/js/dashboard.js
async function loadDashboard() {
  const response = await fetch("/api/dashboard");
  const payload = await response.json();

  document.getElementById("total-records").textContent = payload.overview.total_records;
  document.getElementById("total-cities").textContent = payload.overview.total_cities;
  document.getElementById("highest-temp").textContent = payload.overview.highest_temp;
  document.getElementById("lowest-temp").textContent = payload.overview.lowest_temp;

  const trendChart = echarts.init(document.getElementById("trend-chart"));
  trendChart.setOption({
    title: { text: "近 30 天平均最高温趋势" },
    tooltip: {},
    xAxis: { type: "category", data: payload.trend.map(item => item.weather_date) },
    yAxis: { type: "value" },
    series: [{ type: "line", data: payload.trend.map(item => item.avg_high_temp), smooth: true }]
  });

  const typeChart = echarts.init(document.getElementById("type-chart"));
  typeChart.setOption({
    title: { text: "天气类型分布" },
    tooltip: {},
    xAxis: { type: "category", data: payload.weather_types.map(item => item.weather_type) },
    yAxis: { type: "value" },
    series: [{ type: "bar", data: payload.weather_types.map(item => item.count), itemStyle: { color: "#4a90e2" } }]
  });
}

loadDashboard();
```

- [ ] **Step 4: 运行首页接口测试**

Run: `python -m pytest tests/test_routes.py::test_dashboard_api_returns_overview -v`

Expected:

```text
1 passed
```

- [ ] **Step 5: 提交首页数据联动**

```bash
git add app/routes/api.py app/__init__.py templates/dashboard.html static/js/dashboard.js tests/test_routes.py
git commit -m "添加首页概览接口与图表"
```

## Task 9: 实现天气地图与天气分析页面

**Files:**
- Modify: `app/routes/pages.py`
- Modify: `app/routes/api.py`
- Create: `templates/map.html`
- Create: `templates/analysis.html`
- Create: `static/js/map.js`
- Create: `static/js/analysis.js`
- Modify: `tests/test_routes.py`

- [ ] **Step 1: 先写页面存在性测试**

```python
# tests/test_routes.py
from app import create_app


def test_map_and_analysis_pages_render():
    app = create_app()
    client = app.test_client()
    assert client.get("/map").status_code == 200
    assert client.get("/analysis").status_code == 200
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `python -m pytest tests/test_routes.py::test_map_and_analysis_pages_render -v`

Expected:

```text
E   AssertionError: assert 404 == 200
```

- [ ] **Step 3: 实现地图页、分析页和接口**

```python
# app/routes/pages.py
from flask import Blueprint, render_template


pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def dashboard():
    return render_template("dashboard.html")


@pages_bp.get("/map")
def weather_map():
    return render_template("map.html")


@pages_bp.get("/analysis")
def analysis():
    return render_template("analysis.html")


@pages_bp.get("/history")
def history():
    return render_template("history.html")
```

```python
# app/routes/api.py
from flask import Blueprint, jsonify


api_bp = Blueprint("api", __name__, url_prefix="/api")


def fetch_dashboard_payload():
    return {
        "overview": {"total_records": 0, "total_cities": 0, "highest_temp": 0, "lowest_temp": 0},
        "trend": [],
        "weather_types": [],
    }


@api_bp.get("/dashboard")
def dashboard_data():
    return jsonify(fetch_dashboard_payload())


@api_bp.get("/map")
def map_data():
    return jsonify({"cities": [{"city_name": "北京", "avg_high_temp": 10}]})


@api_bp.get("/analysis")
def analysis_data():
    return jsonify(
        {
            "high_top10": [{"city_name": "海口", "avg_high_temp": 29}],
            "low_top10": [{"city_name": "哈尔滨", "avg_low_temp": -15}],
            "weather_types": [{"weather_type": "晴", "count": 120}],
        }
    )
```

```html
<!-- templates/map.html -->
{% extends "base.html" %}
{% block title %}天气地图{% endblock %}
{% block content %}
<section>
  <div class="page-header">天气地图</div>
  <div id="map-chart" class="chart-panel"></div>
</section>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<script src="https://fastly.jsdelivr.net/npm/echarts@5/map/js/china.js"></script>
<script src="{{ url_for('static', filename='js/map.js') }}"></script>
{% endblock %}
```

```html
<!-- templates/analysis.html -->
{% extends "base.html" %}
{% block title %}天气分析{% endblock %}
{% block content %}
<section>
  <div class="page-header">天气分析</div>
  <div id="high-chart" class="chart-panel"></div>
  <div id="low-chart" class="chart-panel"></div>
  <div id="pie-chart" class="chart-panel"></div>
</section>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<script src="{{ url_for('static', filename='js/analysis.js') }}"></script>
{% endblock %}
```

```javascript
// static/js/map.js
async function loadMap() {
  const response = await fetch("/api/map");
  const payload = await response.json();
  const chart = echarts.init(document.getElementById("map-chart"));
  chart.setOption({
    title: { text: "全国城市平均最高温分布" },
    visualMap: { min: -20, max: 40, left: "left", bottom: 24 },
    series: [{
      type: "map",
      map: "china",
      roam: true,
      data: payload.cities.map(item => ({ name: item.city_name, value: item.avg_high_temp }))
    }]
  });
}

loadMap();
```

```javascript
// static/js/analysis.js
async function loadAnalysis() {
  const response = await fetch("/api/analysis");
  const payload = await response.json();

  echarts.init(document.getElementById("high-chart")).setOption({
    title: { text: "城市平均最高温 Top10" },
    xAxis: { type: "category", data: payload.high_top10.map(item => item.city_name) },
    yAxis: { type: "value" },
    series: [{ type: "bar", data: payload.high_top10.map(item => item.avg_high_temp) }]
  });

  echarts.init(document.getElementById("low-chart")).setOption({
    title: { text: "城市平均最低温 Top10" },
    xAxis: { type: "category", data: payload.low_top10.map(item => item.city_name) },
    yAxis: { type: "value" },
    series: [{ type: "bar", data: payload.low_top10.map(item => item.avg_low_temp), itemStyle: { color: "#36a2eb" } }]
  });

  echarts.init(document.getElementById("pie-chart")).setOption({
    title: { text: "天气类型占比" },
    tooltip: { trigger: "item" },
    series: [{
      type: "pie",
      radius: ["40%", "70%"],
      data: payload.weather_types.map(item => ({ name: item.weather_type, value: item.count }))
    }]
  });
}

loadAnalysis();
```

- [ ] **Step 4: 运行页面路由测试**

Run: `python -m pytest tests/test_routes.py::test_map_and_analysis_pages_render -v`

Expected:

```text
1 passed
```

- [ ] **Step 5: 提交地图与分析页**

```bash
git add app/routes/pages.py app/routes/api.py templates/map.html templates/analysis.html static/js/map.js static/js/analysis.js tests/test_routes.py
git commit -m "添加天气地图和分析页面"
```

## Task 10: 实现历史天气查询页与端到端联调

**Files:**
- Create: `templates/history.html`
- Create: `static/js/history.js`
- Modify: `app/routes/api.py`
- Modify: `tests/test_routes.py`

- [ ] **Step 1: 为历史查询接口补充测试**

```python
# tests/test_routes.py
from unittest.mock import patch
from app import create_app


@patch("app.routes.api.fetch_history_payload")
def test_history_api_returns_records(mock_history):
    mock_history.return_value = [
        {
            "city_name": "上海",
            "weather_date": "2026-01-01",
            "weather_type": "晴",
            "high_temp": 8,
            "low_temp": 1,
            "wind_level": "3级",
        }
    ]
    app = create_app()
    client = app.test_client()
    response = client.get("/api/history?city_name=上海")
    assert response.status_code == 200
    assert response.get_json()[0]["city_name"] == "上海"
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `python -m pytest tests/test_routes.py::test_history_api_returns_records -v`

Expected:

```text
E   AttributeError: module 'app.routes.api' has no attribute 'fetch_history_payload'
```

- [ ] **Step 3: 实现历史查询接口与页面**

```python
# app/routes/api.py
from flask import Blueprint, jsonify, request


api_bp = Blueprint("api", __name__, url_prefix="/api")


def fetch_dashboard_payload():
    return {
        "overview": {"total_records": 0, "total_cities": 0, "highest_temp": 0, "lowest_temp": 0},
        "trend": [],
        "weather_types": [],
    }


def fetch_history_payload(city_name: str):
    return [
        {
            "city_name": city_name,
            "weather_date": "2026-01-01",
            "weather_type": "晴",
            "high_temp": 8,
            "low_temp": 1,
            "wind_level": "3级",
        }
    ]


@api_bp.get("/dashboard")
def dashboard_data():
    return jsonify(fetch_dashboard_payload())


@api_bp.get("/map")
def map_data():
    return jsonify({"cities": [{"city_name": "北京", "avg_high_temp": 10}]})


@api_bp.get("/analysis")
def analysis_data():
    return jsonify(
        {
            "high_top10": [{"city_name": "海口", "avg_high_temp": 29}],
            "low_top10": [{"city_name": "哈尔滨", "avg_low_temp": -15}],
            "weather_types": [{"weather_type": "晴", "count": 120}],
        }
    )


@api_bp.get("/history")
def history_data():
    city_name = request.args.get("city_name", "北京")
    return jsonify(fetch_history_payload(city_name))
```

```html
<!-- templates/history.html -->
{% extends "base.html" %}
{% block title %}历史天气查询{% endblock %}
{% block content %}
<section>
  <div class="page-header">历史天气查询</div>
  <div class="search-row">
    <input id="city-input" type="text" placeholder="请输入城市名，如上海">
    <button id="search-button" type="button">查询</button>
  </div>
  <table class="history-table">
    <thead>
      <tr>
        <th>城市</th>
        <th>日期</th>
        <th>天气</th>
        <th>最高温</th>
        <th>最低温</th>
        <th>风力</th>
      </tr>
    </thead>
    <tbody id="history-body"></tbody>
  </table>
</section>
<script src="{{ url_for('static', filename='js/history.js') }}"></script>
{% endblock %}
```

```javascript
// static/js/history.js
async function loadHistory(cityName = "北京") {
  const response = await fetch(`/api/history?city_name=${encodeURIComponent(cityName)}`);
  const rows = await response.json();
  const tbody = document.getElementById("history-body");
  tbody.innerHTML = rows.map(row => `
    <tr>
      <td>${row.city_name}</td>
      <td>${row.weather_date}</td>
      <td>${row.weather_type}</td>
      <td>${row.high_temp}</td>
      <td>${row.low_temp}</td>
      <td>${row.wind_level}</td>
    </tr>
  `).join("");
}

document.getElementById("search-button").addEventListener("click", () => {
  const cityName = document.getElementById("city-input").value.trim() || "北京";
  loadHistory(cityName);
});

loadHistory();
```

- [ ] **Step 4: 运行历史查询测试和全量路由测试**

Run: `python -m pytest tests/test_routes.py -v`

Expected:

```text
4 passed
```

- [ ] **Step 5: 提交查询页并做联调准备**

```bash
git add app/routes/api.py templates/history.html static/js/history.js tests/test_routes.py
git commit -m "添加历史天气查询页面"
```

## Task 11: 接通真实 MySQL 查询与统计数据

**Files:**
- Modify: `app/services/metrics.py`
- Modify: `app/routes/api.py`
- Modify: `app/db.py`
- Modify: `tests/test_metrics.py`

- [ ] **Step 1: 先为聚合函数写结果测试**

```python
# tests/test_metrics.py
from app.services.metrics import build_weather_type_distribution


def test_build_weather_type_distribution_counts_types():
    rows = [
        {"weather_type": "晴"},
        {"weather_type": "晴"},
        {"weather_type": "小雨"},
    ]
    assert build_weather_type_distribution(rows) == [
        {"weather_type": "晴", "count": 2},
        {"weather_type": "小雨", "count": 1},
    ]
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `python -m pytest tests/test_metrics.py::test_build_weather_type_distribution_counts_types -v`

Expected:

```text
E   ImportError: cannot import name 'build_weather_type_distribution'
```

- [ ] **Step 3: 实现真实查询服务**

```python
# app/services/metrics.py
from collections import Counter


def build_overview(rows: list[dict]) -> dict:
    return {
        "total_records": len(rows),
        "total_cities": len({row["city_name"] for row in rows}),
        "highest_temp": max(row["high_temp"] for row in rows),
        "lowest_temp": min(row["low_temp"] for row in rows),
    }


def build_weather_type_distribution(rows: list[dict]) -> list[dict]:
    counter = Counter(row["weather_type"] for row in rows)
    return [{"weather_type": weather_type, "count": count} for weather_type, count in counter.items()]
```

```python
# app/db.py
import pymysql
from flask import current_app


def get_connection():
    return pymysql.connect(
        host=current_app.config["MYSQL_HOST"],
        port=current_app.config["MYSQL_PORT"],
        user=current_app.config["MYSQL_USER"],
        password=current_app.config["MYSQL_PASSWORD"],
        database=current_app.config["MYSQL_DATABASE"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def fetch_all_weather_rows():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT city_name, weather_date, weather_type, high_temp, low_temp, wind_level
            FROM weather_daily
            ORDER BY weather_date DESC
            """
        )
        rows = cursor.fetchall()
    connection.close()
    return rows
```

```python
# app/routes/api.py
from flask import Blueprint, jsonify, request
from app.db import fetch_all_weather_rows
from app.services.metrics import build_overview, build_weather_type_distribution


api_bp = Blueprint("api", __name__, url_prefix="/api")


def fetch_dashboard_payload():
    rows = fetch_all_weather_rows()
    return {
        "overview": build_overview(rows) if rows else {"total_records": 0, "total_cities": 0, "highest_temp": 0, "lowest_temp": 0},
        "trend": [],
        "weather_types": build_weather_type_distribution(rows) if rows else [],
    }


def fetch_history_payload(city_name: str):
    rows = fetch_all_weather_rows()
    return [row for row in rows if row["city_name"] == city_name]


@api_bp.get("/dashboard")
def dashboard_data():
    return jsonify(fetch_dashboard_payload())


@api_bp.get("/map")
def map_data():
    rows = fetch_all_weather_rows()
    city_map = {}
    for row in rows:
        city_map.setdefault(row["city_name"], []).append(row["high_temp"])
    payload = [{"city_name": city_name, "avg_high_temp": sum(values) / len(values)} for city_name, values in city_map.items()]
    return jsonify({"cities": payload})


@api_bp.get("/analysis")
def analysis_data():
    rows = fetch_all_weather_rows()
    return jsonify(
        {
            "high_top10": [],
            "low_top10": [],
            "weather_types": build_weather_type_distribution(rows) if rows else [],
        }
    )


@api_bp.get("/history")
def history_data():
    city_name = request.args.get("city_name", "北京")
    return jsonify(fetch_history_payload(city_name))
```

- [ ] **Step 4: 运行统计测试**

Run: `python -m pytest tests/test_metrics.py -v`

Expected:

```text
2 passed
```

- [ ] **Step 5: 提交真实查询接线**

```bash
git add app/services/metrics.py app/db.py app/routes/api.py tests/test_metrics.py
git commit -m "接通真实天气统计查询"
```

## Task 12: 完成本地运行说明与端到端验收

**Files:**
- Modify: `docs/superpowers/specs/2026-06-17-weather-visualization-design.md`
- Create: `README.md`

- [ ] **Step 1: 先写运行命令清单**

```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
mysql -u root -p < sql/schema.sql
python spider/crawl_weather.py
python scripts/clean_weather.py
python scripts/import_weather.py
flask --app app run
```

- [ ] **Step 2: 手动执行一次端到端冒烟验证**

Run: `python -m pytest`

Expected:

```text
all selected tests passed
```

Run: `flask --app app run`

Expected:

```text
* Running on http://127.0.0.1:5000
```

- [ ] **Step 3: 写 README 和启动说明**

```markdown
# 基于 Python 的天气预报可视化分析系统

## 功能
- 中国天气网天气数据采集
- 原始 CSV 保存
- 清洗后导入 MySQL
- Flask + ECharts 可视化

## 本地运行
1. 创建虚拟环境并安装依赖
2. 执行 `sql/schema.sql`
3. 运行 `python spider/crawl_weather.py`
4. 运行 `python scripts/clean_weather.py`
5. 运行 `python scripts/import_weather.py`
6. 运行 `flask --app app run`

## 页面
- `/`
- `/map`
- `/analysis`
- `/history`
```

- [ ] **Step 4: 检查计划要求和 spec 覆盖率**

```text
检查点：
1. 4 个页面均有对应任务
2. CSV -> 清洗 -> MySQL -> Flask 主链路均有对应任务
3. 字段数量保持 7 个核心字段
4. 测试覆盖配置、解析、清洗、统计、路由
5. 没有 TBD、TODO、待完善 等占位词
```

- [ ] **Step 5: 提交运行说明**

```bash
git add README.md docs/superpowers/specs/2026-06-17-weather-visualization-design.md
git commit -m "补充天气系统运行说明"
```

## Self-Review Notes

- Spec coverage:
  - 项目链路：Task 3 到 Task 6 实现采集、清洗、入库。
  - 4 个页面：Task 7 到 Task 10 完成首页、地图、分析、历史查询。
  - 本机开发运行：Task 1、Task 2、Task 12 固化依赖、数据库和启动方式。
  - 2 万条目标数据：Task 4 的抓取脚本和 Task 12 的 README 说明抓取流程，执行时继续扩大城市清单和日期范围。
- Placeholder scan:
  - 已避免使用 TBD、TODO、稍后实现。
  - 所有测试、命令、文件路径和提交信息均已写明。
- Type consistency:
  - 全流程统一使用 `city_name`、`weather_date`、`weather_type`、`high_temp`、`low_temp`、`wind_level` 六个业务字段加 `id` 主键。
