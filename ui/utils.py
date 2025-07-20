# -*- coding: utf-8 -*-

"""
UI相关的辅助工具模块
"""

from PySide6.QtWidgets import QMessageBox

def show_message(title, text, icon_type=QMessageBox.Information, parent=None):
    """
    显示一个简单的消息提示框。
    :param title: 弹窗标题
    :param text: 弹窗内容
    :param icon_type: 图标类型 (Information, Warning, Critical)
    :param parent: 父窗口
    """
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.setIcon(icon_type)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec()
