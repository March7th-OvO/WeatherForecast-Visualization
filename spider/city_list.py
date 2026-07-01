"""
城市列表加载模块。

通过中国天气网的三级 JSON 接口获取全国城市/站点的编码和省份信息。
优先从本地 JSON 文件读取（毫秒级），本地文件不存在时才走 HTTP。

API 层级结构（中国天气网城市编码体系）：
    省 (china.html) → 市 (provshi/{province_code}.html) → 区县/站点 (station/{city_prefix}.html)

每条城市记录包含 city_name（站点名）、city_code（天气编码）、province_name（所属省份）。

数据文件：
    data/city_codes.json —— 持久化的城市编码列表（首次由爬虫生成，后续直接读取）
"""

import json
from pathlib import Path

import requests


# ---- 持久化文件路径 ----
# 项目根目录 / data / city_codes.json
_CITY_CODES_FILE = Path(__file__).resolve().parent.parent / "data" / "city_codes.json"

# ---- 默认城市列表（网络不可用且本地文件不存在时的兜底数据） ----
# 包含 10 个主要城市的基本信息，确保极端情况下系统仍可运行
DEFAULT_CITY_CODES = [
    {"city_name": "北京", "city_code": "101010100", "province_name": "北京"},
    {"city_name": "上海", "city_code": "101020100", "province_name": "上海"},
    {"city_name": "广州", "city_code": "101280101", "province_name": "广东"},
    {"city_name": "深圳", "city_code": "101280601", "province_name": "广东"},
    {"city_name": "成都", "city_code": "101270101", "province_name": "四川"},
    {"city_name": "杭州", "city_code": "101210101", "province_name": "浙江"},
    {"city_name": "武汉", "city_code": "101200101", "province_name": "湖北"},
    {"city_name": "南京", "city_code": "101190101", "province_name": "江苏"},
    {"city_name": "西安", "city_code": "101110101", "province_name": "陕西"},
    {"city_name": "重庆", "city_code": "101040100", "province_name": "重庆"},
]

# 请求头：声明 User-Agent 标识爬虫身份
HEADERS = {
    "User-Agent": "Mozilla/5.0 WeatherVisualization/1.0",
}


def load_city_codes(limit: int = 100) -> list[dict]:
    """
    加载全国城市/站点编码列表。

    加载优先级：
    1. 本地 data/city_codes.json —— 毫秒级，无网络依赖
    2. 中国天气网 API —— 数百次 HTTP 请求，耗时 30s+
    3. 内置默认列表 —— 仅 10 个城市，极端兜底

    Args:
        limit: 最多返回的城市/站点数量，默认 100

    Returns:
        [{"city_name": "北京", "city_code": "101010100", "province_name": "北京"}, ...]
    """
    # ---- 第一优先：本地 JSON 文件 ----
    if _CITY_CODES_FILE.exists():
        try:
            with open(_CITY_CODES_FILE, "r", encoding="utf-8") as fh:
                all_codes = json.load(fh)
            return all_codes[:limit]
        except (json.JSONDecodeError, OSError):
            # 文件损坏或不可读，继续尝试 HTTP
            pass

    # ---- 第二优先：中国天气网 API ----
    try:
        codes = _load_city_codes_from_weather(limit)
        # 异步持久化不阻塞返回（失败静默忽略）
        _persist_city_codes(codes)
        return codes
    except requests.RequestException:
        # 网络请求失败，返回默认列表作为最后兜底
        return DEFAULT_CITY_CODES[:limit]


def refresh_city_codes_file(limit: int = 5000) -> list[dict]:
    """
    强制从中国天气网 API 刷新本地城市编码文件。

    用于数据维护场景（如爬虫脚本定时更新），不走本地缓存，
    直接拉取最新数据并覆盖 data/city_codes.json。

    Args:
        limit: 拉取上限，默认 5000（覆盖全国所有站点）

    Returns:
        城市编码列表
    """
    codes = _load_city_codes_from_weather(limit)
    _persist_city_codes(codes)
    return codes


def _load_city_codes_from_weather(limit: int) -> list[dict]:
    """
    从中国天气网三级 JSON 接口逐层加载城市编码。

    加载流程：
    1. 第一层：获取全国省份列表（china.html）
    2. 第二层：遍历每个省份，获取其下辖城市列表（provshi/{省编码}.html）
    3. 第三层：遍历每个城市，获取其下辖区县/站点列表（station/{城市前缀}.html）

    城市编码规则：
    - 省会城市（city_suffix == "00"）：编码 = 省编码 + 站后缀 + "00"
      例如：北京 (101) + 00 → 101010100
    - 普通站点：编码 = 省编码 + 市后缀 + 站后缀

    Args:
        limit: 达到此数量后提前返回，避免加载全部 2000+ 站点

    Returns:
        城市编码列表
    """
    # ---- 第一层：省份 ----
    provinces = _load_json("https://www.weather.com.cn/data/city3jdata/china.html")
    cities: list[dict] = []

    for province_code, province_name in provinces.items():
        # ---- 第二层：该省下辖的城市 ----
        province_cities = _load_json(
            f"https://www.weather.com.cn/data/city3jdata/provshi/{province_code}.html"
        )

        for city_suffix in province_cities.keys():
            # 城市前缀 = 省编码 + 市后缀，用于拼接第三层 URL
            city_prefix = f"{province_code}{city_suffix}"

            # ---- 第三层：该城市下辖的区县/站点 ----
            stations = _load_json(
                f"https://www.weather.com.cn/data/city3jdata/station/{city_prefix}.html"
            )

            for station_suffix, station_name in stations.items():
                # 中国天气网编码规则：
                # 当 city_suffix == "00" 时表示省会/直辖市的直接站点
                if city_suffix == "00":
                    station_code = f"{province_code}{station_suffix}00"
                else:
                    station_code = f"{city_prefix}{station_suffix}"

                cities.append(
                    {
                        "city_name": station_name,
                        "city_code": station_code,
                        "province_name": province_name,
                    }
                )

                # 达到数量上限，提前返回
                if len(cities) >= limit:
                    return cities

    return cities


def _load_json(url: str) -> dict:
    """
    发送 GET 请求并解析 JSON 响应。

    Args:
        url: 中国天气网城市数据接口地址

    Returns:
        解析后的 JSON 字典

    Raises:
        requests.RequestException: 网络请求失败时向上抛出
    """
    response = requests.get(url, headers=HEADERS, timeout=20)
    # HTTP 状态码非 2xx 时抛出异常
    response.raise_for_status()
    # 强制设置为 UTF-8，防止自动检测错误导致乱码
    response.encoding = "utf-8"
    return json.loads(response.text)


def _persist_city_codes(codes: list[dict]) -> None:
    """
    将城市编码列表持久化到本地 JSON 文件。

    写入 data/city_codes.json，供后续 load_city_codes() 直接读取，
    避免每次启动都走数百次 HTTP 请求。

    Args:
        codes: 城市编码列表
    """
    try:
        _CITY_CODES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(_CITY_CODES_FILE, "w", encoding="utf-8") as fh:
            json.dump(codes, fh, ensure_ascii=False, indent=2)
    except OSError:
        # 写入失败不阻塞主流程（下次请求会重新尝试 HTTP）
        pass
