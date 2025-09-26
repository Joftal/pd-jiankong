#!/usr/bin/env python3
"""
简化版构建脚本 - 避免复杂的依赖问题
专注于核心功能，确保程序能正常运行
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# 设置UTF-8编码以支持Unicode字符
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def check_dependencies():
    """检查必要的依赖"""
    try:
        import PyInstaller
        print("[CHECK] PyInstaller 已安装")
    except ImportError:
        print("[ERROR] PyInstaller 未安装")
        print("请运行: pip install pyinstaller")
        return False
    
    # 检查必要的文件
    required_files = [
        "main.py",
        "database_manager.py", 
        "notification_manager.py",
        "panda_monitor.py",
        "config.py",
        "user_settings.py",
        "requirements.txt"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"[ERROR] 缺少文件: {file}")
            return False
        else:
            print(f"[CHECK] 找到文件: {file}")
    
    return True

def clean_build():
    """清理构建目录"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"[CHECK] 清理目录: {dir_name}")
    
    # 清理spec文件
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"[CHECK] 清理文件: {spec_file}")

def build_executable():
    """构建可执行文件"""
    print("🔨 开始构建可执行文件...")
    
    # PyInstaller 命令参数 - 简化版
    cmd = [
        "pyinstaller",
        "--onedir",                     # 打包成目录（包含所有依赖）
        "--windowed",                   # Windows下不显示控制台
        "--name=PD-Signal",             # 可执行文件名称
        "--distpath=dist",              # 输出目录
        "--workpath=build",             # 临时文件目录
        "--clean",                      # 清理临时文件
        "--noconfirm",                  # 不询问确认
        "--log-level=WARN",             # 设置日志级别为WARN，减少输出
        "--noupx",                      # 禁用UPX压缩，避免兼容性问题
        "--add-data", "requirements.txt;.",  # 添加数据文件
    ]
    
    # 添加用户设置文件（如果存在）
    if Path("usersetting.json").exists():
        cmd.extend(["--add-data", "usersetting.json;."])
    
    # 只收集必要的模块，避免复杂依赖
    essential_modules = [
        "flet",
        "requests", 
        "plyer",
        "sqlite3",
        "urllib3",
        "certifi",
        "charset_normalizer",
        "idna"
    ]
    
    for module in essential_modules:
        cmd.extend(["--collect-all", module])
    
    # 隐藏导入 - 只包含核心必要的
    hidden_imports = [
        "sqlite3",
        "plyer.platforms.win.notification",
        "plyer.platforms.win",
        "plyer.platforms",
        "flet.core",
        "requests",
        "urllib3",
        "certifi",
        "charset_normalizer",
        "idna"
    ]
    
    for import_name in hidden_imports:
        cmd.extend(["--hidden-import", import_name])
    
    # 排除有问题的模块
    excludes = [
        "tkinter",
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "PIL",
        "cv2",
        "tensorflow",
        "torch",
        "sklearn",
        "pytest",  # 排除pytest避免构建错误
        "setuptools.tests",
        "pkg_resources.tests"
    ]
    
    for exclude in excludes:
        cmd.extend(["--exclude-module", exclude])
    
    # 主文件
    cmd.append("main.py")
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("[CHECK] 构建成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def create_startup_script():
    """创建启动脚本"""
    batch_content = '''@echo off
chcp 65001 >nul
echo ========================================
echo    PD Signal - PandaLive监控工具
echo ========================================
echo.
echo 正在启动程序...
echo.

cd /d "%~dp0"
if exist "PD-Signal.exe" (
    echo ✅ 找到可执行文件，正在启动...
    PD-Signal.exe
) else (
    echo ❌ 错误: 未找到 PD-Signal.exe
    echo 请确保文件完整
)

echo.
echo 程序已退出
pause
'''
    
    with open("dist/启动PD-Signal.bat", "w", encoding="utf-8") as f:
        f.write(batch_content)
    
    print("[CHECK] 创建启动脚本: 启动PD-Signal.bat")

def create_readme():
    """创建使用说明"""
    readme_content = """# PD Signal - PandaLive监控工具

## 使用说明

1. 首次运行需要设置Cookie：
   - 打开浏览器，登录 PandaLive
   - 按F12打开开发者工具
   - 切换到Network标签
   - 刷新页面，找到任意请求
   - 复制请求头中的Cookie值
   - 粘贴到应用的Cookie设置中

2. 添加监控主播：
   - 在"主播ID"输入框中输入要监控的主播ID
   - 点击"添加"按钮

3. 开始监控：
   - 确保已设置有效Cookie
   - 点击"开始监控"按钮
   - 程序会自动检查主播状态并发送系统通知

## 功能特点

- [OK] 支持多主播同时监控
- [OK] 实时开播/下播通知
- [OK] Windows系统通知
- [OK] 数据持久化存储
- [OK] 现代化GUI界面
- [OK] 配置自动保存

## 注意事项

- 需要有效的PandaLive Cookie才能正常工作
- 建议设置合理的检测间隔，避免请求过于频繁
- 程序会自动保存配置和监控列表
- 日志文件会自动在程序目录创建

## 故障排除

如果程序无法启动，请尝试：

1. 使用"启动PD-Signal.bat"查看详细错误信息
2. 检查是否有杀毒软件阻止程序运行
3. 确保Windows版本支持（Windows 10或更高版本）
4. 检查程序目录权限

## 技术支持

如有问题，请检查：
1. Cookie是否有效
2. 网络连接是否正常
3. 主播ID是否正确
4. 查看程序目录下的log.txt文件获取详细日志

版本: 1.0.0 (简化版)
构建时间: {build_time}
"""
    
    from datetime import datetime
    build_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open("dist/使用说明.txt", "w", encoding="utf-8") as f:
        f.write(readme_content.format(build_time=build_time))
    
    print("[CHECK] 创建使用说明: 使用说明.txt")

def create_debug_script():
    """创建调试脚本"""
    debug_content = '''@echo off
chcp 65001 >nul
echo ========================================
echo    PD Signal 调试模式
echo ========================================
echo.
echo 此脚本将显示详细的错误信息
echo.

cd /d "%~dp0"
if exist "PD-Signal.exe" (
    echo ✅ 找到可执行文件
    echo 正在以调试模式启动...
    echo.
    
    REM 设置环境变量以显示更多调试信息
    set PYTHONPATH=%CD%
    set PYTHONIOENCODING=utf-8
    
    REM 运行程序并捕获输出
    PD-Signal.exe 2>&1
    
) else (
    echo ❌ 错误: 未找到 PD-Signal.exe
    echo 请确保文件完整
)

echo.
echo 调试信息已显示完毕
pause
'''
    
    with open("dist/调试模式.bat", "w", encoding="utf-8") as f:
        f.write(debug_content)
    
    print("[CHECK] 创建调试脚本: 调试模式.bat")

def main():
    """主函数"""
    print("[START] PD Signal 简化版构建工具")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("[ERROR] 依赖检查失败，请先安装必要的依赖")
        sys.exit(1)
    
    # 清理构建目录
    clean_build()
    
    # 构建可执行文件
    if not build_executable():
        print("[ERROR] 构建失败")
        sys.exit(1)
    
    # 创建额外文件
    create_startup_script()
    create_readme()
    create_debug_script()
    
    print("\n" + "=" * 50)
    print("[SUCCESS] 构建完成！")
    print(f"[FOLDER] 输出目录: {Path('dist').absolute()}")
    print("[LIST] 输出文件:")
    
    # 列出dist目录中的所有内容
    dist_path = Path("dist")
    if dist_path.exists():
        for item in dist_path.iterdir():
            if item.is_file():
                size = item.stat().st_size / 1024 / 1024  # MB
                print(f"   - {item.name} ({size:.1f} MB)")
            elif item.is_dir():
                print(f"   - {item.name}/ (目录)")
                # 列出目录中的主要文件
                try:
                    for subitem in item.iterdir():
                        if subitem.is_file():
                            size = subitem.stat().st_size / 1024 / 1024  # MB
                            print(f"     - {subitem.name} ({size:.1f} MB)")
                except PermissionError:
                    print(f"     - (无法访问目录内容)")
    
    print("\n[TIP] 提示:")
    print("   - 运行 dist/PD-Signal/PD-Signal.exe 启动程序")
    print("   - 使用 dist/启动PD-Signal.bat 可以查看控制台输出")
    print("   - 使用 dist/调试模式.bat 可以查看详细错误信息")
    print("   - 阅读 dist/使用说明.txt 了解详细使用方法")
    print("   - 此版本已简化依赖，避免构建错误")

if __name__ == "__main__":
    main()
