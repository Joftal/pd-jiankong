#!/usr/bin/env python3
"""
构建脚本 - 将Python应用打包为可执行文件
使用PyInstaller进行打包
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_dependencies():
    """检查必要的依赖"""
    try:
        import PyInstaller
        print("✓ PyInstaller 已安装")
    except ImportError:
        print("❌ PyInstaller 未安装")
        print("请运行: pip install pyinstaller")
        return False
    
    # 检查必要的文件
    required_files = [
        "main.py",
        "database_manager.py", 
        "notification_manager.py",
        "panda_monitor.py",
        "config.py",
        "requirements.txt"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ 缺少文件: {file}")
            return False
        else:
            print(f"✓ 找到文件: {file}")
    
    return True

def clean_build():
    """清理构建目录"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.spec"]
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"✓ 清理目录: {dir_name}")
    
    # 清理spec文件
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"✓ 清理文件: {spec_file}")

def create_icon():
    """创建应用图标（如果不存在）"""
    icon_path = Path("icon.ico")
    if not icon_path.exists():
        print("⚠️  未找到icon.ico，将使用默认图标")
        return None
    return str(icon_path)

def build_executable():
    """构建可执行文件"""
    print("🔨 开始构建可执行文件...")
    
    # PyInstaller 命令参数
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包成单个文件
        "--windowed",                   # Windows下不显示控制台
        "--name=PD-Signal",             # 可执行文件名称
        "--distpath=dist",              # 输出目录
        "--workpath=build",             # 临时文件目录
        "--clean",                      # 清理临时文件
    ]
    
    # 添加图标
    icon_path = create_icon()
    if icon_path:
        cmd.extend(["--icon", icon_path])
    
    # 添加数据文件
    cmd.extend([
        "--add-data", "requirements.txt;.",
    ])
    
    # 隐藏导入
    hidden_imports = [
        "sqlite3",
        "plyer.platforms.win.notification",
        "flet.core",
        "requests"
    ]
    
    for import_name in hidden_imports:
        cmd.extend(["--hidden-import", import_name])
    
    # 主文件
    cmd.append("main.py")
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ 构建成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def create_installer():
    """创建安装包（可选）"""
    print("📦 创建安装包...")
    
    # 这里可以添加NSIS或其他安装包创建工具的调用
    # 暂时只是创建一个简单的批处理文件
    
    batch_content = '''@echo off
echo 正在启动 PD Signal...
cd /d "%~dp0"
PD-Signal.exe
pause
'''
    
    with open("dist/启动PD-Signal.bat", "w", encoding="gbk") as f:
        f.write(batch_content)
    
    print("✓ 创建启动脚本: 启动PD-Signal.bat")

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

- ✅ 支持多主播同时监控
- ✅ 实时开播/下播通知
- ✅ Windows系统通知
- ✅ 数据持久化存储
- ✅ 现代化GUI界面
- ✅ 配置自动保存

## 注意事项

- 需要有效的PandaLive Cookie才能正常工作
- 建议设置合理的检测间隔，避免请求过于频繁
- 程序会自动保存配置和监控列表

## 技术支持

如有问题，请检查：
1. Cookie是否有效
2. 网络连接是否正常
3. 主播ID是否正确

版本: 1.0.0
构建时间: {build_time}
"""
    
    from datetime import datetime
    build_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open("dist/使用说明.txt", "w", encoding="utf-8") as f:
        f.write(readme_content.format(build_time=build_time))
    
    print("✓ 创建使用说明: 使用说明.txt")

def main():
    """主函数"""
    print("🚀 PD Signal 构建工具")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败，请先安装必要的依赖")
        sys.exit(1)
    
    # 清理构建目录
    clean_build()
    
    # 构建可执行文件
    if not build_executable():
        print("❌ 构建失败")
        sys.exit(1)
    
    # 创建额外文件
    create_installer()
    create_readme()
    
    print("\n" + "=" * 50)
    print("🎉 构建完成！")
    print(f"📁 输出目录: {Path('dist').absolute()}")
    print("📋 输出文件:")
    
    for file in Path("dist").iterdir():
        if file.is_file():
            size = file.stat().st_size / 1024 / 1024  # MB
            print(f"   - {file.name} ({size:.1f} MB)")
    
    print("\n💡 提示:")
    print("   - 运行 PD-Signal.exe 启动程序")
    print("   - 使用 启动PD-Signal.bat 可以看到控制台输出")
    print("   - 阅读 使用说明.txt 了解详细使用方法")

if __name__ == "__main__":
    main()
