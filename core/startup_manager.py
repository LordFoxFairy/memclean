# -*- coding: utf-8 -*-

"""
Windows 启动项管理模块
- 负责在注册表中添加或删除程序的开机自启项。
- 此功能仅在程序被打包成 .exe 后才能正常工作。
"""

import sys
import os
import winreg as reg

# 程序的最终名称，需要与打包时的 --name 参数一致
APP_NAME = "memclean"


def set_startup(enabled: bool):
    """
    在注册表中设置或移除开机自启项。
    :param enabled: True表示设置自启，False表示移除。
    :return: 一个元组 (bool, str)，表示成功与否和提示信息。
    """
    # HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    try:
        # 只有在程序被打包后 (frozen) 才执行此操作
        if not hasattr(sys, 'frozen'):
            message = "开机自启功能仅在程序被打包成 .exe 后生效。"
            print(f"Warning: {message}")
            # 在开发环境中，我们可以返回一个提示，而不是报错
            return True, message

        # sys.executable 是打包后 .exe 文件的绝对路径
        app_path = sys.executable
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_WRITE)

        if enabled:
            # 将程序的路径写入注册表
            reg.SetValueEx(key, APP_NAME, 0, reg.REG_SZ, f'"{app_path}"')
            reg.CloseKey(key)
            print(f"已设置开机自启: {app_path}")
            return True, "已成功设置开机自启。"
        else:
            # 从注册表中删除键值
            reg.DeleteValue(key, APP_NAME)
            reg.CloseKey(key)
            print("已取消开机自启。")
            return True, "已成功取消开机自启。"

    except FileNotFoundError:
        # 如果要删除的键值本身就不存在，也算操作成功
        if not enabled:
            return True, "未找到自启项，无需取消。"
        return False, "无法找到注册表启动项路径。"
    except Exception as e:
        return False, f"操作注册表失败: {e}"

