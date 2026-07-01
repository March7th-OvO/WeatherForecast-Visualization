"""
Pytest 全局 Fixtures（测试夹具）。

conftest.py 是 pytest 的特殊文件，其中定义的 fixtures 会被同目录下
所有测试文件自动发现和共享，无需显式导入。

当前提供的 fixtures：
    app: 创建测试模式的 Flask 应用实例
"""

import pytest

from app import create_app


@pytest.fixture()
def app():
    """
    创建 Flask 测试应用实例。

    使用 create_app() 工厂函数创建应用后，开启 TESTING 模式：
    - Flask 内部异常不会被全局错误处理器吞掉
    - 便于在测试中直接捕获和断言异常
    """
    flask_app = create_app()
    flask_app.config.update(TESTING=True)
    return flask_app
