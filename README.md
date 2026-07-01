# 基于 Python 的天气预报可视化分析系统

## 项目简介

本项目是一个基于 Python + Flask + ECharts 的天气预报可视化分析系统，数据来源于中国天气网。系统抓取全国城市 15 天天气预报数据，经清洗后通过 Flask 提供 Web 页面，使用 ECharts 展示数据大屏、城市地图、统计分析和历史查询四类可视化图表。项目采用纯 CSV 方案运行，不依赖 MySQL，部署轻量。

**主要功能**
- 数据大屏：全国温度 / 天气 / 风速 / 湿度总览
- 城市地图：各城市天气分布可视化
- 深度分析：多维度统计对比图表
- 历史查询：按城市与日期精确检索

**数据规模**
- 覆盖 1370 个城市/站点
- 15 天预报数据
- 清洗后约 20,550 条记录

**技术栈**
- 语言：Python
- Web 框架：Flask
- 可视化：ECharts
- 数据处理：Pandas
- 数据来源：中国天气网爬虫

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

## 部署到服务器

项目采用纯 CSV 模式运行，不依赖 MySQL，部署非常轻量。以下提供几种常见部署方案。

无论哪种方案，部署前都先准备好 Python 环境和项目依赖：

```bash
# 1. 克隆项目到服务器
git clone <仓库地址> /path/to/WeatherForecastSystem
cd /path/to/WeatherForecastSystem

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Linux / macOS:
source venv/bin/activate
# Windows PowerShell:
# .\venv\Scripts\Activate.ps1

# 4. 安装依赖
pip install -r requirements.txt

# 5. 配置 .env
# 拷贝或创建 .env 文件，至少设置 CLEAN_DATA_FILE 和 SECRET_KEY
# 参考项目根目录的 .env.example

# 6. 确认清洗后的数据已放在 data/clean/ 目录下
```

完成后，再选择下方任意一种方案启动服务。

### 方案一：Waitress（推荐，Windows / Linux 通用）

[Waitress](https://docs.pylonsproject.org/projects/waitress/) 是纯 Python 的生产级 WSGI 服务器，Windows 和 Linux 都能用，无需额外编译。

```bash
# 安装
pip install waitress

# 启动（在项目根目录，虚拟环境已激活）
waitress-serve --host=0.0.0.0 --port=5000 app:create_app
```

启动后访问 `http://服务器IP:5000/` 即可。

### 方案二：Gunicorn（仅 Linux）

```bash
# 安装
pip install gunicorn

# 启动（在项目根目录，虚拟环境已激活）
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

参数说明：
- `-w 4`：4 个工作进程，根据服务器 CPU 核数调整
- `-b 0.0.0.0:5000`：监听所有网卡的 5000 端口

### 方案三：Docker 部署

在项目根目录创建 `Dockerfile`：

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

# 确保清洗后的数据目录存在
RUN mkdir -p data/clean

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```

构建并运行：

```bash
# 构建镜像
docker build -t weather-forecast .

# 运行容器（请修改 CLEAN_DATA_FILE 路径为容器内的路径）
docker run -d \
  --name weather-app \
  -p 5000:5000 \
  -e CLEAN_DATA_FILE=data/clean/weather_clean_20260617_160504.csv \
  -e SECRET_KEY=your-strong-secret-key \
  weather-forecast
```

> **注意**：Docker 部署时需要将清洗后的 CSV 数据复制到镜像内，或通过挂载卷 (`-v`) 将宿主机上的 `data/clean/` 目录挂载到容器内。

### 方案四：系统服务（Linux + systemd）

创建服务文件 `/etc/systemd/system/weather-forecast.service`：

```ini
[Unit]
Description=天气预报可视化分析系统
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/WeatherForecastSystem
Environment=CLEAN_DATA_FILE=data/clean/weather_clean_20260617_160504.csv
Environment=SECRET_KEY=your-strong-secret-key
ExecStart=/usr/local/bin/gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now weather-forecast
```

### 部署注意事项

1. **修改 SECRET_KEY**：生产环境务必修改 `.env` 中的 `SECRET_KEY` 为一个随机字符串
2. **数据文件路径**：确保 `CLEAN_DATA_FILE` 指向服务器上正确的清洗 CSV 文件路径；如果不设置，系统会自动使用 `data/clean/` 下最新的文件
3. **防火墙**：确保服务器防火墙开放了对应端口（如 5000）
4. **反向代理**（可选）：建议用 Nginx 做反向代理，提供 HTTPS 和静态资源缓存

Nginx 反向代理配置参考：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/WeatherForecastSystem/static/;
        expires 7d;
    }
}
```

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

本次实际验证结果已经通过：

- `1370` 个城市/站点
- `15` 天天气数据
- 清洗后可直接供 Flask 使用的 `20550` 条记录

## 📄 许可

本项目基于 [MIT License](LICENSE) 开源。
