; ===================================================================
;  Inno Setup Script for MemClean (最终版)
;  Author: Your Name
;  Version: 1.0
; ===================================================================
;  此脚本用于 Inno Setup Compiler 来创建一个专业的安装程序。
;  在使用此脚本前，请确保：
;  1. 您已经运行了 build.py 脚本。
;  2. 'dist\memclean.exe' 文件已经成功生成。
;  3. 此脚本与 build.py 在同一个目录下。
; ===================================================================

[Setup]
AppId={{F0C3E5A6-0B6C-4A7D-8B3E-3F2E9A0C1D8B}
AppName=MemClean
AppVersion=1.0
AppPublisher=Your Name
DefaultDirName={autopf}\MemClean
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=memclean-setup-v1.0
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\memclean.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
; 默认使用英文界面，以保证最大兼容性
; Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimp.isl"

[Tasks]
; 在这里定义安装过程中的可选任务
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startup"; Description: "开机时自动启动 MemClean"; GroupDescription: "启动选项:"; Flags: checkedonce

[Files]
Source: "dist\memclean.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\MemClean"; Filename: "{app}\memclean.exe"
Name: "{autodesktop}\MemClean"; Filename: "{app}\memclean.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\memclean.exe"; Description: "{cm:LaunchProgram,MemClean}"; Flags: nowait postinstall skipifsilent

; 新增 [Registry] 段，用于根据用户的选择写入注册表
[Registry]
; Root: HKCU 指当前用户，Subkey 指启动项的注册表路径
; ValueName 是我们程序的名字，ValueData 是程序的完整路径
; Tasks: startup 表示只有当用户勾选了名为 "startup" 的任务时，才会执行此操作
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "MemClean"; ValueData: """{app}\memclean.exe"""; Tasks: startup

[UninstallDelete]
; 卸载时，自动删除程序生成的配置文件
Type: files; Name: "{localappdata}\memclean\config.json"
Type: filesandordirs; Name: "{localappdata}\memclean"
