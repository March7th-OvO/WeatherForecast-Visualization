# 基于 Python 的天气预报可视化分析系统

## 项目简介

这是一个基于 `Python + Flask + Pandas + ECharts` 的天气预报可视化分析系统，数据来源为中国天气网。

当前运行主线已经切换为纯 CSV 方案：

`中国天气网 -> 原始 CSV -> 清洗 CSV -> Flask 页面 -> ECharts 图表`

也就是说，项目现在**不依赖 MySQL** 就能完整运行。

## 已实现功能

- 中国天气网城市层级接口抓取
- 中国天气网 15 天天气页面抓取
- 原始天气数据保存为 CSV
- 清洗脚本去重并统一字段
- Flask 4 个页面与 API
- ECharts 首页、地图、分析、历史查询图表
- 默认直接读取最新清洗后的 CSV
- 单元测试 `14` 项通过

## 目录结构

```text
app/                Flask 应用
spider/             天气爬虫
scripts/            清洗、导入、MySQL 启停脚本
sql/                建表脚本（可选，不再是运行必需）
templates/          页面模板
static/             CSS 与 JS
data/raw/           原始 CSV
data/clean/         清洗后 CSV
docs/               设计文档与实现计划
tests/              Pytest 测试
```

## 安装依赖

```powershell
python -m pip install -r requirements.txt
```

## 推荐运行方式

### 1. 抓取天气数据

```powershell
python -m spider.crawl_weather --max-cities 1400
```

说明：

- 当前爬虫稳定抓取中国天气网 `15 天` 页面
- `1400` 个城市/站点大约能得到 `2 万+` 条原始数据

### 2. 清洗原始 CSV

```powershell
python -m scripts.clean_weather --input data/raw/weather_raw_20260617_160504.csv --output data/clean/weather_clean_20260617_160504.csv
```

如果你重新抓了一批新数据，也可以不手动指定，直接运行：

```powershell
python -m scripts.clean_weather
```

### 3. 配置 `.env`

在项目根目录创建 `.env`，内容参考 [.env.example](C:/Users/27316/Documents/New%20project%206/.env.example)。

纯 CSV 版最关键的是这一个变量：

```env
CLEAN_DATA_FILE=data/clean/weather_clean_20260617_160504.csv
SECRET_KEY=weather-secret-key
```

如果不写 `CLEAN_DATA_FILE`，系统会自动读取 `data/clean/` 目录里最新的一份 `weather_clean_*.csv`。

### 4. 启动 Flask

```powershell
flask --app app run
```

默认访问：

- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/map`
- `http://127.0.0.1:5000/analysis`
- `http://127.0.0.1:5000/history`

## 测试

```powershell
python -m pytest -v
```

## 已验证结果

已完成的真实验证：

- `python -m pytest -v`
- `python -m spider.crawl_weather --max-cities 1400`
- `python -m scripts.clean_weather --input data/raw/weather_raw_20260617_160504.csv --output data/clean/weather_clean_20260617_160504.csv`
- Flask 直接从 CSV 读取并返回 `/api/dashboard`
- Flask 直接从 CSV 读取并返回 `/api/analysis`
- Flask 直接从 CSV 读取并返回 `/api/history`

当前真实样本结果：

- 总记录数：`20550`
- 城市数：`1370`
- 最高温：`44`
- 最低温：`-4`

## 可选项

仓库里仍然保留了：

- `scripts/import_weather.py`
- `sql/schema.sql`
- `scripts/start_local_mysql.ps1`
- `scripts/stop_local_mysql.ps1`

这些现在都只是可选扩展，不再是项目运行必需。

## 说明

由于中国天气网当前可稳定抓取的是 `15 天` 页面，所以代码当前采用：

- 扩大城市/站点数量来达到 `2 万条` 目标
- 而不是一次性实现 `100 城市 × 200 天` 的历史回溯抓取

本次实际验证结果已经通过：

- `1370` 个城市/站点
- `15` 天天气数据
- 清洗后可直接供 Flask 使用的 `20550` 条记录
