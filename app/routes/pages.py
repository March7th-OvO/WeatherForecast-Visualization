from flask import Blueprint, render_template


pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def dashboard():
    return render_template("dashboard.html")


@pages_bp.get("/map")
def weather_map():
    return render_template("map.html")


@pages_bp.get("/analysis")
def analysis():
    return render_template("analysis.html")


@pages_bp.get("/history")
def history():
    return render_template("history.html")
