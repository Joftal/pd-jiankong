#!/usr/bin/env python3
"""
修复版构建脚本 - 解决PD-Signal.exe无限循环创建进程的问题
使用PyInstaller进行打包，包含所有必要的依赖
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
    files_to_clean = ["*.spec"]
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"[CHECK] 清理目录: {dir_name}")
    
    # 清理spec文件
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"[CHECK] 清理文件: {spec_file}")

def create_icon():
    """创建应用图标（如果不存在）"""
    icon_path = Path("icon.ico")
    if not icon_path.exists():
        print("[WARNING] 未找到icon.ico，将使用默认图标")
        return None
    return str(icon_path)

def build_executable():
    """构建可执行文件"""
    print("🔨 开始构建可执行文件...")
    
    # PyInstaller 命令参数 - 修复版（包含所有依赖）
    cmd = [
        "pyinstaller",
        "--onedir",                     # 打包成目录（包含所有依赖）
        "--windowed",                   # Windows下不显示控制台
        "--name=PD-Signal",             # 可执行文件名称
        "--distpath=dist",              # 输出目录
        "--workpath=build",             # 临时文件目录
        "--clean",                      # 清理临时文件
        "--noconfirm",                  # 不询问确认
        "--log-level=INFO",             # 设置日志级别
        "--noupx",                      # 禁用UPX压缩，避免兼容性问题
        "--collect-all=flet",           # 收集flet的所有模块
        "--collect-all=requests",       # 收集requests的所有模块
        "--collect-all=plyer",          # 收集plyer的所有模块
        "--collect-all=unicodedata",    # 收集Unicode数据支持
        "--collect-all=sqlite3",        # 收集sqlite3的所有模块
        "--collect-all=asyncio",        # 收集asyncio的所有模块
        "--collect-all=threading",      # 收集threading的所有模块
        "--collect-all=logging",        # 收集logging的所有模块
        "--collect-all=json",           # 收集json的所有模块
        "--collect-all=datetime",       # 收集datetime的所有模块
        "--collect-all=pathlib",        # 收集pathlib的所有模块
        "--collect-all=platform",       # 收集platform的所有模块
        "--collect-all=webbrowser",     # 收集webbrowser的所有模块
        "--collect-all=typing",         # 收集typing的所有模块
        "--collect-all=collections",    # 收集collections的所有模块
        "--collect-all=functools",      # 收集functools的所有模块
        "--collect-all=itertools",      # 收集itertools的所有模块
        "--collect-all=operator",       # 收集operator的所有模块
        "--collect-all=re",             # 收集re的所有模块
        "--collect-all=sys",            # 收集sys的所有模块
        "--collect-all=traceback",      # 收集traceback的所有模块
        "--collect-all=warnings",       # 收集warnings的所有模块
        "--collect-all=weakref",        # 收集weakref的所有模块
        "--collect-all=copy",           # 收集copy的所有模块
        "--collect-all=pickle",         # 收集pickle的所有模块
        "--collect-all=io",             # 收集io的所有模块
        "--collect-all=base64",         # 收集base64的所有模块
        "--collect-all=hashlib",        # 收集hashlib的所有模块
        "--collect-all=hmac",           # 收集hmac的所有模块
        "--collect-all=ssl",            # 收集ssl的所有模块
        "--collect-all=socket",         # 收集socket的所有模块
        "--collect-all=http",           # 收集http的所有模块
        "--collect-all=email",          # 收集email的所有模块
        "--collect-all=mimetypes",      # 收集mimetypes的所有模块
        "--collect-all=tempfile",       # 收集tempfile的所有模块
        "--collect-all=shutil",         # 收集shutil的所有模块
        "--collect-all=glob",           # 收集glob的所有模块
        "--collect-all=fnmatch",        # 收集fnmatch的所有模块
        "--collect-all=stat",           # 收集stat的所有模块
        "--collect-all=subprocess",     # 收集subprocess的所有模块
        "--collect-all=signal",         # 收集signal的所有模块
        "--collect-all=atexit",         # 收集atexit的所有模块
        "--collect-all=contextlib",     # 收集contextlib的所有模块
        "--collect-all=inspect",        # 收集inspect的所有模块
        "--collect-all=importlib",      # 收集importlib的所有模块
        "--collect-all=pkg_resources",  # 收集pkg_resources的所有模块
        "--collect-all=setuptools",     # 收集setuptools的所有模块
    ]
    
    # 添加图标
    icon_path = create_icon()
    if icon_path:
        cmd.extend(["--icon", icon_path])
    
    # 添加数据文件
    cmd.extend([
        "--add-data", "requirements.txt;.",
    ])
    
    # 隐藏导入 - 精简版，只包含必要的
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
        "idna",
        "unicodedata",  # Unicode数据支持
        "codecs",       # 编码支持
        "locale"        # 本地化支持
    ]
    
    for import_name in hidden_imports:
        cmd.extend(["--hidden-import", import_name])
    
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

## 技术支持

如有问题，请检查：
1. Cookie是否有效
2. 网络连接是否正常
3. 主播ID是否正确
4. 查看程序目录下的log.txt文件获取详细日志

版本: 1.0.0 (修复版)
构建时间: {build_time}
"""
    
    from datetime import datetime
    build_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open("dist/使用说明.txt", "w", encoding="utf-8") as f:
        f.write(readme_content.format(build_time=build_time))
    
    print("[CHECK] 创建使用说明: 使用说明.txt")

def main():
    """主函数"""
    print("[START] PD Signal 修复版构建工具")
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
    create_readme()
    
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
    print("   - 阅读 dist/使用说明.txt 了解详细使用方法")
    print("   - 此版本包含所有依赖文件，确保程序正常运行")
    print("   - 已修复无限循环创建进程的问题")

if __name__ == "__main__":
    main()
