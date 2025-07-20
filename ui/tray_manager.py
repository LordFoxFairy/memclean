# -*- coding: utf-8 -*-

"""
系统托盘图标管理模块 (最终视觉优化版)
- 采用独立数据线程和阻塞式采样，数据与任务管理器完全同步。
- 根据用户配置，动态显示CPU或内存使用率。
- 双击图标直接执行清理，单击无反应。
"""
import math
import psutil
import time
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtCore import Qt, Signal, QTimer, QObject, QThread, QRect
from PySide6.QtGui import QPainter, QColor, QFont, QIcon, QPixmap, QPen, QBrush

# 导入配置加载器和新的通知窗口
from core.config_manager import load_config
from .notification import NotificationWidget


class StatsWorker(QObject):
    """在独立线程中运行的数据采集器"""
    stats_updated = Signal(float, float)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        """循环采集数据"""
        while self.running:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().percent
            if not self.running:
                break
            self.stats_updated.emit(cpu, mem)

    def stop(self):
        self.running = False


class TrayManager(QSystemTrayIcon):
    # 定义信号
    show_main_window_requested = Signal()
    show_settings_requested = Signal()
    cleanup_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = load_config()
        self.current_notification = None

        # --- 预创建绘图资源 ---
        self.font = QFont("Segoe UI", 22, QFont.Bold)
        self.bg_color = QColor(0, 0, 0, 0)
        self.progress_bg_pen = QPen(QColor(0, 0, 0, 50), 5)
        self.progress_pen = QPen(QColor(), 5.5)
        self.text_pen = QPen(QColor(0, 0, 0))

        # --- 设置托盘菜单 ---
        self.menu = QMenu()
        self.menu.addAction("显示主窗口").triggered.connect(self.show_main_window_requested.emit)
        self.menu.addAction("设置").triggered.connect(self.show_settings_requested.emit)
        self.menu.addSeparator()
        self.menu.addAction("一键加速 (Alt+Alt)").triggered.connect(self.cleanup_requested.emit)
        self.menu.addSeparator()
        self.menu.addAction("退出").triggered.connect(self.stop_and_quit)
        self.setContextMenu(self.menu)

        self.activated.connect(self.on_activated)

        # --- 创建并启动数据采集线程 ---
        self.thread = QThread()
        self.worker = StatsWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.stats_updated.connect(self.update_icon)
        self.thread.start()

        self.update_icon(0, 0)
        self.show()

    def reload_config(self):
        self.config = load_config()

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.cleanup_requested.emit()

    def show_custom_notification(self, message):
        """创建并显示自定义通知，并采用更稳定的生命周期管理"""
        # 如果当前有通知正在显示，先立刻关闭它
        if self.current_notification:
            self.current_notification.close()

        tray_icon_rect = self.geometry()
        if not tray_icon_rect.isValid():
            screen = self.parent().primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                tray_icon_rect = QRect(screen_geometry.width() - 150, screen_geometry.height() - 60, 22, 22)

        # 创建一个新的通知实例
        notification = NotificationWidget()
        self.current_notification = notification  # 持有对新通知的引用

        # 当新通知被销毁时，清空引用
        notification.destroyed.connect(self._clear_notification_ref)

        notification.show_notification(message, tray_icon_rect)

    def _clear_notification_ref(self):
        """【新】用于清空通知引用的槽函数"""
        self.current_notification = None

    def update_icon(self, cpu_val, mem_val):
        display_metric = self.config.get("display_metric", "mem")

        if display_metric == "cpu":
            primary_val, primary_name, secondary_val, secondary_name = cpu_val, "CPU", mem_val, "内存"
        else:
            primary_val, primary_name, secondary_val, secondary_name = mem_val, "内存", cpu_val, "CPU"

        size = 64
        pixmap = QPixmap(size, size)
        pixmap.fill(self.bg_color)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = pixmap.rect().adjusted(1, 1, -1, -1)
        painter.setPen(self.progress_bg_pen)
        painter.drawEllipse(rect)

        if primary_val < 60:
            self.progress_pen.setColor(QColor("#27AE60"))
        elif primary_val < 85:
            self.progress_pen.setColor(QColor("#F39C12"))
        else:
            self.progress_pen.setColor(QColor("#C0392B"))

        painter.setPen(self.progress_pen)
        span_angle = primary_val / 100.0 * 360 * 16
        painter.drawArc(rect, 90 * 16, -span_angle)

        painter.setPen(self.text_pen)
        painter.setFont(self.font)
        painter.drawText(rect, Qt.AlignCenter, str(int(primary_val)))
        painter.end()

        self.setIcon(QIcon(pixmap))
        self.setToolTip(f"{primary_name}: {int(primary_val)}%\n{secondary_name}: {int(secondary_val)}%\n(双击加速)")

    def stop_worker_thread(self):
        if self.thread.isRunning():
            self.worker.stop()
            self.thread.quit()
            self.thread.wait(1000)

    def stop_and_quit(self):
        self.parent().instance().quit()
