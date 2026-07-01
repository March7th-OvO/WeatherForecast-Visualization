"""
服务包 —— 数据统计与指标计算。

提供纯 Python 实现的数据聚合函数，不依赖数据库。
"""

from app.services.metrics import build_overview

__all__ = ["build_overview"]
