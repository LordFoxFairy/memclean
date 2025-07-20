# -*- coding: utf-8 -*-

"""
自定义通知窗口
- 一个无边框、半透明、带圆角的提示框，会自动定位和消失。
"""

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect

class NotificationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置窗口属性：无边框、工具窗口（不在任务栏显示）、总在最前
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowStaysOnTopHint
        )
        # 设置背景透明，以便我们可以绘制圆角
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # 使用QSS设置样式，模仿截图效果
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 0.9);
                color: white;
                border-radius: 6px;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("padding: 8px 12px; font-size: 10pt;")
        self.layout.addWidget(self.label)

        # 用于淡出效果的动画
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(400) # 动画时长
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.finished.connect(self.close)

    def show_notification(self, text, position_rect, duration=2500):
        """
        显示通知。
        :param text: 要显示的文本 (支持富文本)
        :param position_rect: 托盘图标的几何位置
        :param duration: 显示时长
        """
        self.label.setText(text)
        self.adjustSize() # 根据内容调整大小

        # 计算位置，使其在托盘图标正上方居中
        x = position_rect.x() + (position_rect.width() - self.width()) / 2
        y = position_rect.y() - self.height() - 10 # 10像素的间距

        # 确保窗口不会超出屏幕边界
        screen = self.screen()
        if screen:
            screen_geometry = screen.availableGeometry()
            if x < screen_geometry.left(): x = screen_geometry.left()
            if x + self.width() > screen_geometry.right(): x = screen_geometry.right() - self.width()
            if y < screen_geometry.top(): y = position_rect.bottom() + 10

        self.move(int(x), int(y))
        self.show()

        # 设置一个定时器，在指定时间后启动淡出动画
        QTimer.singleShot(duration, self.animation.start)

