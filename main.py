"""
TVBox 源检查和 JSON 生成工具

这是一个用于检查 TVBox 源是否可用并生成 tvbox.json 和 my.json 的工具。
"""

from src.app import App


if __name__ == "__main__":
    """程序主入口，创建 App 实例并执行"""
    app = App()
    app.run()
