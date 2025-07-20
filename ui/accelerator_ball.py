# -*- coding: utf-8 -*-

"""
“加速球”悬浮窗的UI实现 (优雅白 & 性能优化版)
- 【性能】预编译绘图资源，避免在paintEvent中重复创建对象，彻底解决拖动卡顿。
- 【视觉】采用全新的纯白主题设计，外观更现代、更精致。
- 【视觉】所有动画和数值显示均采用平滑算法。
"""
import math
from PySide6.QtWidgets import QWidget, QMenu, QMessageBox, QApplication
from PySide6.QtCore import Qt, QTimer, QPoint, Signal
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QLinearGradient, QRadialGradient, QFont, QPainterPath

# 从项目其他模块导入
from core.system_monitor import get_system_stats, clean_memory
from .utils import show_message


class AcceleratorBall(QWidget):
    show_main_window_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(90, 90)

        self._is_dragging = False
        self._drag_start_position = QPoint()

        # --- 数据与动画状态 ---
        self.raw_cpu = 0
        self.raw_mem = 0
        self.smoothed_cpu = 0.0
        self.smoothed_mem = 0.0
        self.wave1_offset = 0
        self.wave2_offset = 0.8

        # --- 性能优化：预先创建绘图资源 ---
        self._setup_drawing_resources()

        # --- 双定时器分离数据和动画 ---
        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self.update_system_data)
        self.data_timer.start(1000)

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.tick_animation)
        self.animation_timer.start(16)  # ~60 FPS

        self.update_system_data()

    def _setup_drawing_resources(self):
        """预先创建所有画笔、画刷、字体等，避免在paintEvent中重复创建。"""
        # 背景画刷
        self.bg_brush = QBrush(QColor("#E0E0E0"))
        # 文字画笔
        self.text_pen = QPen(QColor(50, 50, 50))
        # 内存百分比字体
        self.mem_font = QFont("Arial", 14, QFont.Bold)
        # CPU百分比字体
        self.cpu_font = QFont("Arial", 8)
        # 水波高光画笔
        self.wave_highlight_pen = QPen(QColor(100, 180, 255, 180), 1.5)
        # 外边框画笔
        self.outer_border_pen = QPen(QColor(0, 0, 0, 30), 2)

    def update_system_data(self):
        """仅负责获取系统原始数据"""
        stats = get_system_stats()
        self.raw_cpu = stats['cpu_percent']
        self.raw_mem = stats['mem_info'].percent

    def tick_animation(self):
        """仅负责更新动画状态和数值平滑"""
        self.smoothed_cpu = self.smoothed_cpu * 0.95 + self.raw_cpu * 0.05
        self.smoothed_mem = self.smoothed_mem * 0.95 + self.raw_mem * 0.05
        self.wave1_offset = (self.wave1_offset + 0.05) % (2 * math.pi)
        self.wave2_offset = (self.wave2_offset + 0.07) % (2 * math.pi)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        # 1. 绘制白色背景球体
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.bg_brush)
        painter.drawEllipse(rect)

        # 2. 绘制内阴影，增加立体感
        inner_shadow_gradient = QRadialGradient(rect.center(), rect.width() / 2)
        inner_shadow_gradient.setColorAt(0.85, QColor(0, 0, 0, 0))
        inner_shadow_gradient.setColorAt(1.0, QColor(0, 0, 0, 40))
        painter.setBrush(inner_shadow_gradient)
        painter.drawEllipse(rect)

        # 创建圆形剪切区
        clip_path = QPainterPath()
        clip_path.addEllipse(rect)
        painter.setClipPath(clip_path)

        # 3. 绘制水体
        water_level = rect.height() * (1 - self.smoothed_mem / 100.0)
        water_path = QPainterPath()
        water_path.moveTo(rect.left(), rect.bottom())
        water_path.lineTo(rect.left(), water_level)
        for x in range(rect.width() + 1):
            wave1 = 3 * math.sin(x * 0.04 + self.wave1_offset)
            wave2 = 2 * math.sin(x * 0.06 + self.wave2_offset)
            water_path.lineTo(x, water_level + wave1 + wave2)
        water_path.lineTo(rect.right(), rect.bottom())
        water_path.closeSubpath()

        water_gradient = QLinearGradient(rect.center().x(), water_level, rect.center().x(), rect.bottom())
        water_gradient.setColorAt(0, QColor(60, 170, 255, 200))
        water_gradient.setColorAt(1, QColor(20, 120, 230, 255))
        painter.fillPath(water_path, water_gradient)

        # 4. 绘制水面高光
        highlight_path = QPainterPath()
        highlight_path.moveTo(rect.left(), water_level)
        for x in range(rect.width() + 1):
            wave1 = 3 * math.sin(x * 0.04 + self.wave1_offset)
            wave2 = 2 * math.sin(x * 0.06 + self.wave2_offset)
            highlight_path.lineTo(x, water_level + wave1 + wave2)
        painter.setPen(self.wave_highlight_pen)
        painter.drawPath(highlight_path)

        # 重置剪切区
        painter.setClipping(False)

        # 5. 绘制文字
        painter.setPen(self.text_pen)
        painter.setFont(self.mem_font)
        painter.drawText(rect, Qt.AlignCenter, f"{int(self.smoothed_mem)}%")
        painter.setFont(self.cpu_font)
        painter.drawText(rect.adjusted(0, -25, 0, -25), Qt.AlignCenter, f"CPU: {int(self.smoothed_cpu)}%")

        # 6. 绘制最外层的边框
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self.outer_border_pen)
        painter.drawEllipse(rect.adjusted(1, 1, -1, -1))

    # --- 鼠标事件和菜单逻辑保持不变 ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._drag_start_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._is_dragging:
            self.move(event.globalPosition().toPoint() - self._drag_start_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_dragging = False
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.perform_cleanup()
        event.accept()

    def perform_cleanup(self):
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

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        show_main_action = menu.addAction("显示主窗口")
        quit_action = menu.addAction("退出程序")
        action = menu.exec(self.mapToGlobal(event.pos()))
        if action == show_main_action:
            self.show_main_window_requested.emit()
        elif action == quit_action:
            QApplication.quit()
