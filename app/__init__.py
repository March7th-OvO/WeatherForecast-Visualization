from flask import Flask, jsonify

from app.config import Config
from app.routes.api import api_bp
from app.routes.pages import pages_bp


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(Config)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    app.register_blueprint(api_bp)
    app.register_blueprint(pages_bp)

    return app
