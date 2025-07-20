# -*- coding: utf-8 -*-

"""
配置管理模块
- 负责读取和保存 config.json 文件。
"""

import json
import os

CONFIG_FILE = 'config.json'

DEFAULT_CONFIG = {
    "auto_clean_enabled": False,
    "clean_interval_minutes": 5,
    "mem_threshold_percent": 80,
    "display_metric": "mem",
    "start_on_boot": False  # 新增：开机自启选项
}


def load_config():
    """加载配置文件。如果文件不存在或损坏，则创建并使用默认值。"""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 确保旧的配置文件也能获得新键值
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
    except (json.JSONDecodeError, IOError):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG


def save_config(config_data):
    """将配置数据保存到文件。"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
    except IOError as e:
        print(f"Error saving config file: {e}")

