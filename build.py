# -*- coding: utf-8 -*-

"""
MemClean 自动化打包脚本 (Python版)
- 检查所需文件是否存在。
- 调用 PyInstaller 进行打包和压缩。
- 提供清晰的进度和错误反馈。
"""

import os
import subprocess
import sys

# --- 打包配置 ---
APP_NAME = "memclean"
MAIN_SCRIPT = "main.py"
ICON_FILE = "icon.ico"  # 请确保您在根目录有一个名为 icon.ico 的图标文件
UPX_DIR = "."  # UPX 工具所在的目录 (当前目录)


def main():
    """主打包函数"""
    print("======================================================")
    print("  MemClean Automatic Packaging Script (Python)")
    print("======================================================")
    print()

    # --- 第1步：检查所需文件 ---
    print("Step 1: Checking for required files...")
    if not os.path.exists(MAIN_SCRIPT):
        print(f"Error: '{MAIN_SCRIPT}' not found. Make sure you are in the project root directory.")
        sys.exit(1)

    if not os.path.exists(ICON_FILE):
        print(f"Warning: '{ICON_FILE}' not found. The executable will have a default icon.")

    upx_path = os.path.join(UPX_DIR, 'upx.exe')
    use_upx = os.path.exists(upx_path)
    if not use_upx:
        print("Warning: upx.exe not found. The final .exe will not be compressed.")

    # --- 第2步：构建并运行 PyInstaller 命令 ---
    print("\nStep 2: Running PyInstaller to create memclean.exe...")
    print("This may take a few minutes. Please be patient.")

    command = [
        'pyinstaller',
        '--name', APP_NAME,
        '--onefile',
        '--windowed',
    ]

    if os.path.exists(ICON_FILE):
        command.extend(['--icon', ICON_FILE])

    if use_upx:
        command.extend(['--upx-dir', UPX_DIR])

    command.append(MAIN_SCRIPT)

    print(f"\nExecuting command: {' '.join(command)}\n")

    try:
        # 使用 subprocess.run 执行命令，实时捕获输出
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                   encoding='utf-8', errors='replace')
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)

    except FileNotFoundError:
        print("Error: 'pyinstaller' command not found.")
        print("Please make sure you have installed PyInstaller: pip install pyinstaller")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("\nAn error occurred during packaging. Please check the output above.")
        sys.exit(1)

    print("\n======================================================")
    print("  Packaging Complete!")
    print("======================================================")
    print(f"\nYour final program '{APP_NAME}.exe' can be found in the 'dist' folder.")
    print("You can now use 'setup.iss' with Inno Setup to create the installer.")


if __name__ == "__main__":
    main()
