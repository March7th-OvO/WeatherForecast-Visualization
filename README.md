# 基于 Python 的天气预报可视化分析系统

## 项目简介

这是一个基于 `Python + Flask + MySQL + ECharts` 的天气预报可视化分析系统，数据来源为中国天气网。

当前实现链路：

`中国天气网 -> 原始 CSV -> 清洗 CSV -> MySQL -> Flask 页面 -> ECharts 图表`

## 已实现功能

- 中国天气网城市层级接口抓取
- 中国天气网 15 天天气页面抓取
- 原始天气数据保存为 CSV
- 清洗脚本去除重复并统一字段
- MySQL 建表脚本
- Flask 4 个页面骨架
- 首页、地图、分析、历史查询 API
- ECharts 图表脚本
- 单元测试 11 项通过

## 目录结构

```text
app/                Flask 应用
spider/             天气爬虫
scripts/            清洗与导入脚本
sql/                建表脚本
templates/          页面模板
static/             CSS 与 JS
data/raw/           原始 CSV
data/clean/         清洗后 CSV
tests/              Pytest 测试
docs/               设计文档与实现计划
```

## 安装依赖

```powershell
python -m pip install -r requirements.txt
```

## 初始化数据库

```powershell
mysql -u root -p < sql/schema.sql
```

如果本机 `mysql` 命令不可用，也可以在图形化工具中执行 [schema.sql](C:/Users/27316/Documents/New%20project%206/sql/schema.sql)。

## 运行步骤

### 1. 抓取天气数据

```powershell
python -m spider.crawl_weather --max-cities 100
```

说明：

- 当前爬虫默认抓取中国天气网 `15 天` 页面
- 如果想扩大量级，可以提高 `--max-cities`
- 例如 `--max-cities 1400` 理论上可达到约 `21000` 条记录

### 2. 清洗原始 CSV

```powershell
python -m scripts.clean_weather
```

也可以指定输入输出路径：

```powershell
python -m scripts.clean_weather --input data/raw/weather_raw_xxx.csv --output data/clean/weather_clean_xxx.csv
```

### 3. 导入 MySQL

```powershell
python -m scripts.import_weather
```

导入脚本默认读取这些环境变量：

- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`

可参考 [.env.example](C:/Users/27316/Documents/New%20project%206/.env.example)。

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

## 当前验证结果

已完成验证：

- `python -m pytest -v`
- `python -m spider.crawl_weather --max-cities 5`
- `python -m scripts.clean_weather`
- Flask `test_client` 访问 `/`、`/health`、`/api/dashboard`

尚未完成验证：

- 本机 MySQL 实际导入
- 导入真实数据后的页面图表联调

原因：

- 当前仓库内没有你的 MySQL 实际账号密码与库状态，我没有强行假设

## 说明

由于中国天气网当前可直接稳定抓取的是 `15 天` 页面，因此代码实现采用：

- `扩大城市/站点数量` 来接近 2 万条目标
- 而不是一次性实现 `100 城市 × 200 天` 的历史回溯抓取

如果你后续确定要严格按 `200 天历史数据` 做，我下一步可以继续补：

- 历史天气补采方案
- 定时增量采集
- MySQL 聚合 SQL
- 页面样式进一步贴近参考图
