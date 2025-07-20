# -*- coding: utf-8 -*-

"""
全局热键管理模块 (高级版)
- 使用 pynput 库实现全局键盘监听，更稳定可靠。
- 支持 "Alt"+"Alt" 双击和 "Ctrl+Alt+C" 组合键。
- 在独立的线程中运行，不影响UI主线程。
"""

import time
from pynput import keyboard
from PySide6.QtCore import QObject, Signal, QThread


class HotkeyWorker(QObject):
    """在工作线程中运行的键盘监听器"""
    alt_alt_triggered = Signal()
    ctrl_alt_c_triggered = Signal()

    def __init__(self):
        super().__init__()
        self.last_alt_press_time = 0
        self.double_press_interval = 0.3  # 300毫秒内算双击

        # 定义 Ctrl+Alt+C 组合键
        self.combo = {keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('c')}
        self.current_keys = set()

    def on_press(self, key):
        """按键按下事件处理"""
        # 处理 Alt+Alt
        if key in [keyboard.Key.alt_l, keyboard.Key.alt_r]:
            current_time = time.time()
            if current_time - self.last_alt_press_time < self.double_press_interval:
                print("Alt+Alt detected!")
                self.alt_alt_triggered.emit()
            self.last_alt_press_time = current_time

        # 处理组合键
        if key in self.combo:
            self.current_keys.add(key)
            if self.current_keys == self.combo:
                print("Ctrl+Alt+C detected!")
                self.ctrl_alt_c_triggered.emit()

    def on_release(self, key):
        """按键释放事件处理"""
        try:
            self.current_keys.remove(key)
        except KeyError:
            pass

    def run(self):
        """启动键盘监听器"""
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()


class HotkeyManager(QObject):
    """主线程中的热键管理器，负责创建和管理工作线程"""
    alt_alt_triggered = Signal()
    ctrl_alt_c_triggered = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread = QThread()
        self.worker = HotkeyWorker()

        # 将worker移动到新线程
        self.worker.moveToThread(self.thread)

        # 连接信号
        self.worker.alt_alt_triggered.connect(self.alt_alt_triggered)
        self.worker.ctrl_alt_c_triggered.connect(self.ctrl_alt_c_triggered)

        # 线程启动时，运行worker的run方法
        self.thread.started.connect(self.worker.run)

        # 启动线程
        self.thread.start()

    def stop(self):
        """停止监听线程"""
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        print("Hotkey listener stopped.")

