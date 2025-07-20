# -*- coding: utf-8 -*-

"""
应用程序主入口
- 恢复了自定义弹窗和清理缓冲功能。
- 整合了开机自启等所有最终功能。
- 【新】增加了智能冷却机制和额外的提示语。
"""

import sys
import ctypes
import os
import psutil
import time  # 导入time模块
from PySide6.QtWidgets import QApplication, QSystemTrayIcon
from PySide6.QtCore import QTimer

# --- 导入所有需要的模块 ---
from ui.main_window import MainWindow
from ui.settings_window import SettingsWindow
from ui.tray_manager import TrayManager
from core.config_manager import load_config
from core.system_monitor import clean_memory
from core.hotkey_manager import HotkeyManager
from core.startup_manager import set_startup


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    if sys.platform == 'win32':
        if not is_admin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)


class MainApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)

        # --- 新增：智能冷却状态 ---
        self.is_cleaning = False
        self.last_cleanup_time = 0
        self.cleanup_cooldown_seconds = 15  # 15秒的智能判断期

        self.config = load_config()
        self.main_window = MainWindow()
        self.settings_window = SettingsWindow()
        self.tray_manager = TrayManager(self)
        self.hotkey_manager = HotkeyManager(self)

        # --- 连接信号 ---
        self.tray_manager.show_main_window_requested.connect(self.main_window.show_and_raise)
        self.tray_manager.show_settings_requested.connect(self.show_settings)
        self.tray_manager.cleanup_requested.connect(self.perform_cleanup_action)
        self.hotkey_manager.alt_alt_triggered.connect(self.perform_cleanup_action)
        self.hotkey_manager.ctrl_alt_c_triggered.connect(self.perform_cleanup_action)
        self.main_window.clean_button.clicked.connect(self.perform_cleanup_action)
        self.settings_window.settings_saved.connect(self.reload_config_and_timer)

        self.auto_clean_timer = QTimer(self)
        self.auto_clean_timer.timeout.connect(self.check_and_auto_clean)

        self.update_timer_interval()

    def perform_cleanup_action(self):
        """执行清理，并增加了双重缓冲逻辑"""
        current_time = time.time()

        # 第一重缓冲：判断是否正在清理
        if self.is_cleaning:
            self.tray_manager.show_custom_notification("正在清理中，请稍候...")
            return

        # 第二重缓冲：判断是否在智能冷却期内
        if current_time - self.last_cleanup_time < self.cleanup_cooldown_seconds:
            self.tray_manager.show_custom_notification("系统已经很干净啦，休息一下吧~")
            return

        # 设置清理状态为True，开始清理
        self.is_cleaning = True

        success, result_data = clean_memory()
        if success:
            # 清理成功后，更新最后清理时间
            self.last_cleanup_time = time.time()
            if isinstance(result_data, dict) and 'freed_mb' in result_data:
                freed = result_data['freed_mb']
                if freed >= 1:
                    message = f"已腾出 <font color='#3498DB'><b>{freed:.1f}MB</b></font> 内存"
                else:
                    message = "系统状态良好，无需清理"
                self.tray_manager.show_custom_notification(message)
        else:
            message = f"清理失败: {str(result_data)}"
            self.tray_manager.show_custom_notification(message)

        # 3秒后将“正在清理”状态重置为False
        QTimer.singleShot(3000, lambda: setattr(self, 'is_cleaning', False))

    def show_settings(self):
        self.settings_window.show()
        self.settings_window.activateWindow()

    def reload_config_and_timer(self):
        """重新加载配置并更新所有相关设置"""
        self.config = load_config()
        self.tray_manager.reload_config()
        self.update_timer_interval()
        set_startup(self.config.get("start_on_boot", False))

    def update_timer_interval(self):
        """根据配置启动或停止定时器"""
        if self.config.get("auto_clean_enabled", False):
            interval_ms = self.config.get("clean_interval_minutes", 5) * 60 * 1000
            self.auto_clean_timer.start(interval_ms)
        else:
            self.auto_clean_timer.stop()

    def check_and_auto_clean(self):
        """检查内存是否超限并自动清理"""
        if not self.config.get("auto_clean_enabled", False):
            return

        # 自动清理不受冷却时间影响
        current_mem_percent = psutil.virtual_memory().percent
        threshold = self.config.get("mem_threshold_percent", 80)
        if current_mem_percent > threshold:
            # 这里我们直接调用清理的核心逻辑，绕过缓冲检查
            self.is_cleaning = True
            clean_memory()
            QTimer.singleShot(3000, lambda: setattr(self, 'is_cleaning', False))

    def quit(self):
        self.hotkey_manager.stop()
        self.tray_manager.stop_worker_thread()
        super().quit()


if __name__ == "__main__":
    run_as_admin()
    app = MainApplication(sys.argv)
    sys.exit(app.exec())
