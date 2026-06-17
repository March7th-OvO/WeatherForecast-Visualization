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
- Flask 4 个页面与 API
- ECharts 首页、地图、分析、历史查询图表脚本
- 本地便携 MySQL 启停脚本
- 单元测试 12 项通过

## 目录结构

```text
app/                Flask 应用
spider/             天气爬虫
scripts/            清洗、导入、MySQL 启停脚本
sql/                建表脚本
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

### 1. 启动项目自带的本地 MySQL

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_local_mysql.ps1
```

这会在项目目录下创建 `.mysql-local/data/`，并启动一个监听 `127.0.0.1:3307` 的便携 MySQL。

默认会自动创建项目账号：

- 用户名：`weatherapp`
- 密码：`weatherapp123`
- 数据库：`weather_visualization`

### 2. 配置环境变量

在项目根目录创建 `.env`，内容参考 [.env.example](C:/Users/27316/Documents/New%20project%206/.env.example)。

如果使用项目自带 MySQL，推荐写成：

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3307
MYSQL_USER=weatherapp
MYSQL_PASSWORD=weatherapp123
MYSQL_DATABASE=weather_visualization
SECRET_KEY=weather-secret-key
```

### 3. 初始化数据库表

```powershell
Get-Content .\sql\schema.sql | mysql -h 127.0.0.1 -P 3307 -u root
```

### 4. 抓取天气数据

```powershell
python -m spider.crawl_weather --max-cities 100
```

说明：

- 当前爬虫稳定抓取中国天气网 `15 天` 页面
- 若按 `15 天 × 100 城市` 抓取，约可得到 `1500` 条数据
- 若想达到 `2 万条` 级别，可继续提高 `--max-cities`，例如 `1400` 左右

### 5. 清洗原始 CSV

```powershell
python -m scripts.clean_weather
```

也可以指定输入输出路径：

```powershell
python -m scripts.clean_weather --input data/raw/weather_raw_xxx.csv --output data/clean/weather_clean_xxx.csv
```

### 6. 导入 MySQL

```powershell
python -m scripts.import_weather
```

### 7. 启动 Flask

```powershell
flask --app app run
```

默认访问：

- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/map`
- `http://127.0.0.1:5000/analysis`
- `http://127.0.0.1:5000/history`

### 8. 停止本地 MySQL

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop_local_mysql.ps1
```

## 测试

```powershell
python -m pytest -v
```

## 已验证结果

已完成的真实验证：

- `python -m pytest -v`
- `python -m spider.crawl_weather --max-cities 5`
- `python -m scripts.clean_weather`
- 本地便携 MySQL 已启动并监听 `3307`
- `schema.sql` 已成功执行到本地便携 MySQL
- `python -m scripts.import_weather` 已真实导入 `75` 条记录
- Flask 实际查询 `/api/dashboard`、`/api/analysis`、`/api/history` 已返回数据库中的真数据

当前样本验证结果：

- 总记录数：`20550`
- 城市数：`1370`
- 最高温：`44`
- 最低温：`-4`

## 说明

由于中国天气网当前可稳定抓取的是 `15 天` 页面，所以代码当前采用：

- 扩大城市/站点数量来逼近 `2 万条`
- 而不是一次性实现 `100 城市 × 200 天` 的历史回溯抓取

本次实际验证结果已经通过：

- `1370` 个城市/站点
- `15` 天天气数据
- 清洗后入库 `20550` 条记录

如果后续要继续增强，我建议下一步做：

- 历史天气补采方案
- 页面样式继续贴近参考图
- 全国地图中文城市名匹配优化
- 更完整的 MySQL 聚合 SQL
