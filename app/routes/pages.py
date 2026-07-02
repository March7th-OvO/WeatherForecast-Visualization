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

from pathlib import Path

from flask import Blueprint, abort, render_template, send_from_directory


# 页面蓝图不设 url_prefix，直接注册到根路径
pages_bp = Blueprint("pages", __name__)

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIST_DIR = BASE_DIR / "frontend" / "dist"


def _render_page(template_name: str):
    """
    优先返回 React 构建产物，未构建时回退到旧 Jinja 模板。

    这样本地只跑 Flask 时仍可查看旧页面；执行 `npm run build` 后，页面路由
    由 React Router 接管，后端继续专注提供 /api/* JSON 数据。
    """
    if (FRONTEND_DIST_DIR / "index.html").exists():
        return send_from_directory(FRONTEND_DIST_DIR, "index.html")

    return render_template(template_name)


@pages_bp.get("/")
def dashboard():
    """首页总览 —— 数据卡片 + 温度趋势 + 天气分布"""
    return _render_page("dashboard.html")


@pages_bp.get("/map")
def weather_map():
    """天气地图 —— 中国地图 + 各省温度着色"""
    return _render_page("map.html")


@pages_bp.get("/analysis")
def analysis():
    """天气分析 —— Top10 排行 + 天气类型占比饼图"""
    return _render_page("analysis.html")


@pages_bp.get("/history")
def history():
    """15日天气查询 —— 按城市名查询 15 天预报明细表格"""
    return _render_page("history.html")


@pages_bp.get("/assets/<path:filename>")
def react_assets(filename: str):
    """提供 Vite 构建后的 JS/CSS 资源。"""
    assets_dir = FRONTEND_DIST_DIR / "assets"
    if not assets_dir.exists():
        abort(404)
    return send_from_directory(assets_dir, filename)


@pages_bp.get("/vendor/<path:filename>")
def react_vendor(filename: str):
    """提供 React 前端 public/vendor 下的地图等静态资源。"""
    vendor_dir = FRONTEND_DIST_DIR / "vendor"
    if not vendor_dir.exists():
        abort(404)
    return send_from_directory(vendor_dir, filename)
