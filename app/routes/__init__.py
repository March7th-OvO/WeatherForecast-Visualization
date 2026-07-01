"""
路由包 —— 集中导出所有 Flask 蓝图。

api_bp:   提供 /api/* JSON 数据接口
pages_bp: 提供页面模板渲染
"""

from app.routes.api import api_bp
from app.routes.pages import pages_bp

__all__ = ["api_bp", "pages_bp"]
