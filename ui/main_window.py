# -*- coding: utf-8 -*-

"""
主窗口的UI实现
- 不再创建和管理悬浮球。
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import QTimer

# 从项目其他模块导入
from core.system_monitor import get_system_stats, clean_memory
from .utils import show_message


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("系统性能监视器")
        self.setGeometry(200, 200, 320, 180)

        # 设置UI布局
        self.layout = QVBoxLayout(self)
        self.cpu_label = QLabel()
        self.mem_label = QLabel()
        self.clean_button = QPushButton("一键加速 (Ctrl+Alt+C)")

        self.layout.addWidget(self.cpu_label)
        self.layout.addWidget(self.mem_label)
        self.layout.addWidget(self.clean_button)

        # 连接按钮点击事件
        self.clean_button.clicked.connect(self.perform_cleanup)

        # 定时器更新主窗口信息
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_info)
        self.timer.start(1000)

        self.update_info()

    def update_info(self):
        """更新主窗口的详细信息"""
        stats = get_system_stats()
        cpu = stats['cpu_percent']
        mem = stats['mem_info']
        mem_total_gb = mem.total / (1024 ** 3)
        mem_used_gb = mem.used / (1024 ** 3)

        self.cpu_label.setText(f"CPU 使用率: {cpu}%")
        self.mem_label.setText(f"内存: {mem_used_gb:.2f} GB / {mem_total_gb:.2f} GB ({mem.percent}%)")

    def perform_cleanup(self):
        """主窗口的清理按钮功能"""
        success, result_data = clean_memory()
        if success:
            if isinstance(result_data, dict) and 'freed_mb' in result_data:
                freed = result_data['freed_mb']
                message = f"深度清理完成！\n成功释放了约 {freed:.1f} MB 内存。" if freed >= 1 else "系统状态良好，无需深度清理。"
                show_message("内存清理", message, QMessageBox.Information, self)
            else:
                message = "操作成功！"
                show_message("内存清理", message, QMessageBox.Information, self)
        else:
            show_message("清理失败", str(result_data), QMessageBox.Warning, self)

    def show_and_raise(self):
        """显示窗口并将其置于顶层"""
        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        """
        重写关闭事件。
        当用户关闭主窗口时，我们只隐藏它，而不是退出整个应用。
        """
        event.ignore()
        self.hide()
