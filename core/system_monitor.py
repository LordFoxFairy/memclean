# -*- coding: utf-8 -*-

"""
核心功能模块 (对齐任务管理器版)
- 采用与主流优化工具类似的三段式深度清理策略，效果显著。
- 【新】优化了CPU使用率的获取方式，使其与任务管理器的数据更一致。
"""

import sys
import psutil
import ctypes
import subprocess
import os
import time

# --- 在模块加载时就初始化CPU使用率计算 ---
# 第一次调用不返回有意义的值，但会设定一个时间点，用于后续计算。
psutil.cpu_percent(interval=None)

def get_system_stats():
    """获取当前的CPU和内存使用率。"""
    return {
        # 后续调用会返回自上次调用以来的CPU使用率，interval=None使其不阻塞
        'cpu_percent': psutil.cpu_percent(interval=None),
        'mem_info': psutil.virtual_memory()
    }

def clean_memory_windows():
    """
    为Windows系统执行专业级、三段式深度内存清理。
    """
    # ... (此部分清理逻辑保持不变) ...
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_SET_QUOTA = 0x0100
    system_whitelist = {
        'system', 'smss.exe', 'csrss.exe', 'wininit.exe', 'winlogon.exe',
        'services.exe', 'lsass.exe'
    }
    own_pid = os.getpid()
    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi
    ntdll = ctypes.WinDLL('ntdll.dll')
    try:
        ntdll.NtSetSystemInformation.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_ulong]
        ntdll.NtSetSystemInformation.restype = ctypes.c_long
    except AttributeError:
        return (False, "无法访问 ntdll.dll 中的关键函数。")
    mem_before = psutil.virtual_memory().used
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() in system_whitelist or proc.pid == own_pid:
                continue
            handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA, False, proc.pid)
            if handle:
                psapi.EmptyWorkingSet(handle)
                kernel32.CloseHandle(handle)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    system_memory_list_info = 80
    modified_page_list_class = ctypes.c_int(8)
    ntdll.NtSetSystemInformation(system_memory_list_info, ctypes.byref(modified_page_list_class), ctypes.sizeof(modified_page_list_class))
    system_purge_standby_list = 3
    ntdll.NtSetSystemInformation(system_purge_standby_list, None, 0)
    time.sleep(0.5)
    mem_after = psutil.virtual_memory().used
    freed_mb = (mem_before - mem_after) / (1024 * 1024)
    if freed_mb < 0: freed_mb = 0
    return (True, {'freed_mb': freed_mb})


def clean_memory():
    """
    执行跨平台的内存清理操作。
    """
    # ... (此部分清理逻辑保持不变) ...
    platform = sys.platform
    if platform == "win32":
        try:
            success, result = clean_memory_windows()
            if success:
                result['cleaned_count'] = result.get('cleaned_count', 'N/A')
                return True, result
            else:
                return False, result
        except Exception as e:
            return (False, f"Windows 内存清理时发生未知错误。\n错误: {e}")
    elif platform == "linux":
        try:
            mem_before = psutil.virtual_memory().used
            subprocess.run(['sync'], check=True, capture_output=True)
            with open('/proc/sys/vm/drop_caches', 'w') as f:
                f.write('3\n')
            time.sleep(0.5)
            mem_after = psutil.virtual_memory().used
            freed_mb = (mem_before - mem_after) / (1024 * 1024)
            if freed_mb < 0: freed_mb = 0
            return (True, {'freed_mb': freed_mb, 'cleaned_count': 'N/A'})
        except (PermissionError, subprocess.CalledProcessError) as e:
            return (False, f"Linux 缓存清理失败，请使用 sudo 运行程序。\n错误: {e}")
    elif platform == "darwin":
        return (False, "macOS 采用先进的内存管理机制，无需手动清理。")
    else:
        return (False, f"不支持在当前操作系统 ({platform}) 上执行此操作。")
