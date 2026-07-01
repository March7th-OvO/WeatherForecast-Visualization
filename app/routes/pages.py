"""
页面蓝图模块 —— 渲染 HTML 模板。

将 URL 路径映射到对应的 Jinja2 模板文件。
页面只负责返回 HTML 骨架，实际数据通过前端 JS 调用 /api/* 接口获取。

路由一览：
    GET /           → 首页总览 (dashboard.html)
    GET /map        → 天气地图 (map.html)
    GET /analysis   → 天气分析 (analysis.html)
    GET /history    → 15日天气查询 (history.html)
"""

from flask import Blueprint, render_template


# 页面蓝图不设 url_prefix，直接注册到根路径
pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def dashboard():
    """首页总览 —— 数据卡片 + 温度趋势 + 天气分布"""
    return render_template("dashboard.html")


@pages_bp.get("/map")
def weather_map():
    """天气地图 —— 中国地图 + 各省温度着色"""
    return render_template("map.html")


@pages_bp.get("/analysis")
def analysis():
    """天气分析 —— Top10 排行 + 天气类型占比饼图"""
    return render_template("analysis.html")


@pages_bp.get("/history")
def history():
    """15日天气查询 —— 按城市名查询 15 天预报明细表格"""
    return render_template("history.html")
