# MemClean - 智能内存与CPU监视器

一款轻量级、智能化的Windows系统性能监视与优化工具。它以一个精致的动态图标驻留在您的任务栏，实时反馈系统状态，并提供强大的一键加速功能，让您的电脑时刻保持最佳性能。

<img width="193" height="160" alt="image" src="https://github.com/user-attachments/assets/8f02df4a-068d-4e04-b8d5-45f4cdba864e" />

<br>

## 目录

- [✨ 核心功能](https://www.google.com/search?q=%23-核心功能)
- [⚙️ 系统要求](https://www.google.com/search?q=%23️-系统要求)
- [🚀 安装与使用 (普通用户)](https://www.google.com/search?q=%23-安装与使用-普通用户)
- [⌨️ 使用指南](https://www.google.com/search?q=%23️-使用指南)
- [👨‍💻 开发者指南 (从源码构建)](https://www.google.com/search?q=%23-开发者指南-从源码构建)
  - [准备环境](https://www.google.com/search?q=%231-准备环境)
  - [准备打包工具](https://www.google.com/search?q=%232-准备打包工具)
  - [构建流程](https://www.google.com/search?q=%233-构建流程)
- [🛠️ 技术栈](https://www.google.com/search?q=%23️-技术栈)
- [📄 许可证](https://www.google.com/search?q=%23-许可证)

## ✨ 核心功能

- **动态任务栏图标**：一个设计精美的圆形进度条图标，永久固定在任务栏右侧，实时显示CPU或内存占用率，让您对系统状态一目了然。
- **专业级内存清理**：采用与主流优化工具类似的三段式深度清理策略，一键释放被占用的内存，效果立竿见影。
- **智能快捷键**：
  - **Alt + Alt**：快速连按两次 `Alt` 键，即可触发一次深度清理。
  - **双击图标**：直接双击任务栏图标，也能快速完成加速。
- **后台自动清理**：在设置中开启后，程序会在后台默默守护。当内存占用超过您设定的阈值时，会自动执行清理，无需任何手动干预。
- **智能冷却机制**：在您手动加速后的一小段时间内，程序会智能判断系统状态。如果系统已经很干净，它会友好地提示您“休息一下”，避免不必要的重复操作。
- **高度可定制**：
  - **显示切换**：您可以自由选择让图标优先显示CPU还是内存占用率。
  - **自动清理配置**：清理的触发阈值和检查间隔时间均可自定义。
  - **开机自启**：支持一键设置开机自动启动。
- **专业安装包**：提供一个完整、专业的 `setup.exe` 安装程序，体验与主流商业软件一致。

## ⚙️ 系统要求

- **操作系统**: Windows 10 或更高版本 (64位)。
- **运行环境**: 无需安装Python，程序已打包为独立可执行文件。

## 🚀 安装与使用 (普通用户)

我们强烈推荐直接下载我们为您打包好的 `.exe` 安装程序。

1. 前往本项目的 [**Releases**](https://github.com/your-username/your-repo/releases) 页面 (请替换为您的链接)。
2. 下载最新的 `memclean-setup-vX.X.exe` 安装文件。
3. 双击运行安装程序，根据向导提示完成安装即可。

## ⌨️ 使用指南

- **启动程序**：通过桌面快捷方式或开始菜单启动“MemClean”。程序将自动在系统托盘区创建一个图标并在后台运行。
- **查看状态**：直接观察任务栏图标的进度条和数字。
- **一键加速**：快速连按两次 `Alt` 键，或双击任务栏图标。
- **打开设置**：右键单击任务栏图标，然后选择“设置”。
- **退出程序**：右键单击任务栏图标，然后选择“退出”。

## 👨‍💻 开发者指南 (从源码构建)

本指南将指导您如何从源代码开始，一步步构建出可执行程序，并最终打包成一个独立的 `.exe` 安装包。

### 1. 准备环境

- **Python**: 访问 [python.org](https://www.python.org/downloads/) 下载并安装 Python 3.9+。**安装时请务必勾选 "Add Python to PATH"**。

- **依赖库**: 在项目根目录下打开命令行，运行：

  ```
  pip install -r requirements.txt
  ```

  (*您需要先创建一个 `requirements.txt` 文件，内容如下:*)

  ```
  PySide6
  psutil
  pynput
  ```

### 2. 准备打包工具

- **PyInstaller**: 用于将Python脚本打包成 `.exe` 文件。

  ```
  pip install pyinstaller
  ```

- **UPX (可选, 推荐)**: 用于压缩最终生成的 `.exe` 文件，大幅减小体积。

  - 访问 [UPX 的官方发布页面](https://github.com/upx/upx/releases) 并下载最新版。
  - 解压后，将 `upx.exe` 放到本项目的根目录下。

- **Inno Setup**: 用于将构建好的程序文件打包成一个用户友好的安装程序。

  - 访问 [Inno Setup 官网](https://jrsoftware.org/isinfo.php) 下载并安装最新稳定版。

### 3. 构建流程

1. **生成可执行文件**: 在项目根目录下运行 `build.py` 脚本。

   ```
   python build.py
   ```

   成功后，最终的 `memclean.exe` 将位于 `dist` 文件夹中。

2. **创建安装包**:

   - 在项目根目录中，找到并**双击 `setup.iss` 文件**。
   - 在打开的 Inno Setup 窗口中，点击菜单栏的 "Build" -> "Compile" (或按 `Ctrl+F9`)。

3. **完成**:

   - 编译成功后，在 `Output` 文件夹中即可找到最终的安装包 `memclean-setup-vX.X.exe`。

## 🛠️ 技术栈

- **核心语言**: Python 3
- **图形界面**: PySide6 (Qt for Python)
- **系统监控**: psutil
- **全局热键**: pynput
- **打包工具**: PyInstaller
- **安装包**: Inno Setup

## 📄 许可证

本项目采用 [MIT License](https://opensource.org/licenses/MIT) 授权。
