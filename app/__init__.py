from flask import Flask, jsonify

from app.config import Config


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return app
