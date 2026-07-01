"""
Flask 应用工厂模块。

采用应用工厂 (Application Factory) 模式创建 Flask 实例，
方便在不同环境（开发 / 测试 / 生产）中复用相同的创建逻辑。
"""

from flask import Flask, jsonify

from app.config import Config
from app.routes.api import api_bp
from app.routes.pages import pages_bp


def create_app() -> Flask:
    """
    创建并配置 Flask 应用实例。

    职责：
    1. 指定模板目录（../templates）和静态资源目录（../static）
    2. 加载 Config 配置对象
    3. 注册 /health 健康检查路由
    4. 注册 API 蓝图（/api/*）和页面蓝图（/*）

    Returns:
        配置完成的 Flask 应用对象，可供 flask --app app run 直接启动。
    """
    app = Flask(
        __name__,
        # 因为 app/ 在项目根目录下一级，模板和静态资源需要向上一级引用
        template_folder="../templates",
        static_folder="../static",
    )
    # 将 Config 对象中的属性注入到 Flask 的 app.config 字典中
    app.config.from_object(Config())

    # ---- 健康检查端点 ----
    # 供运维或自动化脚本检测服务是否正常运行
    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    # ---- 注册蓝图 ----
    # api_bp：所有 /api/ 前缀的数据接口
    # pages_bp：所有页面路由 (/、/map、/analysis、/history)
    app.register_blueprint(api_bp)
    app.register_blueprint(pages_bp)

    return app
