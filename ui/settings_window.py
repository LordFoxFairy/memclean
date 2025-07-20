# -*- coding: utf-8 -*-

"""
设置面板窗口的UI实现
- 增加了托盘图标显示内容的设置选项。
- 增加了开机自启的设置选项。
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QCheckBox,
                               QLabel, QSpinBox, QPushButton, QGroupBox,
                               QRadioButton)
from PySide6.QtCore import Qt, Signal
from core.config_manager import load_config, save_config

class SettingsWindow(QWidget):
    settings_saved = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.setFixedSize(350, 350) # 调整窗口大小

        main_layout = QVBoxLayout(self)

        # --- 启动设置 ---
        startup_group = QGroupBox("启动设置")
        startup_layout = QVBoxLayout()
        self.startup_checkbox = QCheckBox("开机时自动启动本程序")
        self.startup_checkbox.setToolTip("此功能仅在程序打包成.exe后生效")
        startup_layout.addWidget(self.startup_checkbox)
        startup_group.setLayout(startup_layout)
        main_layout.addWidget(startup_group)

        # --- 显示设置 ---
        display_group = QGroupBox("托盘图标显示设置")
        display_layout = QHBoxLayout()
        display_layout.addWidget(QLabel("优先显示:"))
        self.mem_radio = QRadioButton("内存使用率")
        self.cpu_radio = QRadioButton("CPU使用率")
        display_layout.addWidget(self.mem_radio)
        display_layout.addWidget(self.cpu_radio)
        display_layout.addStretch()
        display_group.setLayout(display_layout)
        main_layout.addWidget(display_group)

        # --- 自动清理设置 ---
        auto_clean_group = QGroupBox("自动清理设置")
        group_layout = QVBoxLayout()
        self.enable_checkbox = QCheckBox("开启自动清理")
        self.enable_checkbox.stateChanged.connect(self.toggle_controls)
        group_layout.addWidget(self.enable_checkbox)
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("当内存占用超过阈值时，每隔"))
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setMinimum(1)
        self.interval_spinbox.setMaximum(120)
        self.interval_spinbox.setSuffix(" 分钟")
        interval_layout.addWidget(self.interval_spinbox)
        interval_layout.addStretch()
        group_layout.addLayout(interval_layout)
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("清理阈值：内存占用超过"))
        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setMinimum(50)
        self.threshold_spinbox.setMaximum(99)
        self.threshold_spinbox.setSuffix(" %")
        threshold_layout.addWidget(self.threshold_spinbox)
        threshold_layout.addStretch()
        group_layout.addLayout(threshold_layout)
        auto_clean_group.setLayout(group_layout)
        main_layout.addWidget(auto_clean_group)

        # --- 按钮 ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.save_button = QPushButton("保存")
        self.cancel_button = QPushButton("取消")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.save_button.clicked.connect(self.save_and_close)
        self.cancel_button.clicked.connect(self.close)

        self.load_settings()

    def load_settings(self):
        config = load_config()
        self.startup_checkbox.setChecked(config.get("start_on_boot", False))
        self.enable_checkbox.setChecked(config.get("auto_clean_enabled", False))
        self.interval_spinbox.setValue(config.get("clean_interval_minutes", 5))
        self.threshold_spinbox.setValue(config.get("mem_threshold_percent", 80))
        if config.get("display_metric", "mem") == "cpu":
            self.cpu_radio.setChecked(True)
        else:
            self.mem_radio.setChecked(True)
        self.toggle_controls()

    def save_and_close(self):
        config = {
            "start_on_boot": self.startup_checkbox.isChecked(),
            "auto_clean_enabled": self.enable_checkbox.isChecked(),
            "clean_interval_minutes": self.interval_spinbox.value(),
            "mem_threshold_percent": self.threshold_spinbox.value(),
            "display_metric": "cpu" if self.cpu_radio.isChecked() else "mem"
        }
        save_config(config)
        self.settings_saved.emit()
        self.close()

    def toggle_controls(self):
        is_enabled = self.enable_checkbox.isChecked()
        self.interval_spinbox.setEnabled(is_enabled)
        self.threshold_spinbox.setEnabled(is_enabled)

    def showEvent(self, event):
        self.load_settings()
        super().showEvent(event)
