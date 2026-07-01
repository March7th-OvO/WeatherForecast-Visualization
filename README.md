# 基于 Python 的天气预报可视化分析系统

## 项目简介

本项目是一个基于 `Python + Flask + MySQL + ECharts` 的天气预报可视化分析系统，数据来源于中国天气网。系统抓取全国城市 15 天天气预报数据，先生成原始 CSV，再清洗为结构化 CSV 并持久化到 MySQL；Flask API 运行时直接查询 MySQL，前端使用 ECharts 渲染数据大屏、城市地图、统计分析和历史查询页面。

当前主链路：

```text
中国天气网 -> 原始 CSV -> 清洗 CSV -> MySQL -> Flask API -> ECharts 图表
```

## 已实现功能

- 中国天气网城市层级接口抓取
- 中国天气网 15 天天气页面抓取
- 原始天气数据保存为 CSV
- 清洗脚本去重并统一字段
- 清洗后的 CSV 自动导入 MySQL
- Flask API 直接从 MySQL 查询渲染数据
- ECharts 首页、地图、分析、历史查询图表
- 单元测试覆盖配置、清洗、MySQL 读取、路由和指标计算

## 目录结构

```text
app/                Flask 应用
spider/             天气爬虫
scripts/            清洗、导入、MySQL 启停脚本
sql/                MySQL 建库建表脚本
templates/          页面模板
static/             CSS 与 JS
data/raw/           原始 CSV
data/clean/         清洗后 CSV 归档
docs/               设计文档与实现计划
tests/              Pytest 测试
```

## 安装依赖

```powershell
python -m pip install -r requirements.txt
```

## 配置 MySQL

在项目根目录创建 `.env`，内容参考 [.env.example](.env.example)：

```env
SECRET_KEY=weather-secret-key
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_DATABASE=weather_visualization
```

如果使用仓库自带的本地 MySQL 启动脚本：

```powershell
.\scripts\start_local_mysql.ps1
```

该脚本默认监听 `127.0.0.1:3307`，并创建 `weatherapp / weatherapp123` 用户。你当前使用的是 `root / 123456`，按上面的 `.env` 配置连接自己的 MySQL 即可。

## 运行流程

### 1. 抓取天气数据

```powershell
python -m spider.crawl_weather --max-cities 1400
```

### 2. 清洗并写入 MySQL

```powershell
python -m scripts.clean_weather
```

清洗脚本会自动选择 `data/raw/` 下最新的 `weather_raw_*.csv`，输出到 `data/clean/`，然后导入 MySQL。也可以手动指定输入输出：

```powershell
python -m scripts.clean_weather --input data/raw/weather_raw_20260617_160504.csv --output data/clean/weather_clean_20260617_160504.csv
```

如果只想生成清洗 CSV，不导入 MySQL：

```powershell
python -m scripts.clean_weather --skip-mysql
```

已有清洗 CSV 时，可以单独导入：

```powershell
python -m scripts.import_weather --input data/clean/weather_clean_20260617_160504.csv
```

导入脚本会自动创建数据库和 `weather_daily` 表，并通过 `(city_name, weather_date)` 唯一键更新重复记录。

### 3. 启动 Flask

```powershell
flask --app app run
```

默认访问：

- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/map`
- `http://127.0.0.1:5000/analysis`
- `http://127.0.0.1:5000/history`

## 手动建表

导入脚本会自动建库建表。若需要手动初始化，也可以执行：

```powershell
mysql -h 127.0.0.1 -P 3306 -u root -p < sql/schema.sql
```

`sql/schema.sql` 使用 `CREATE TABLE IF NOT EXISTS`，不会删除已有数据。

## 测试

```powershell
python -m pytest -v
```

## 部署提示

生产部署时需要准备：

- Python 环境和 `requirements.txt` 依赖
- 可访问的 MySQL 服务
- `.env` 中正确的 `MYSQL_*` 和 `SECRET_KEY`
- 已通过 `scripts.clean_weather` 或 `scripts.import_weather` 写入 MySQL 的天气数据

可使用 Waitress 或 Gunicorn 运行 Flask：

```bash
waitress-serve --host=0.0.0.0 --port=5000 app:create_app
```

```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

## 许可

本项目基于 [GNU Affero General Public License v3.0](LICENSE) 开源。
