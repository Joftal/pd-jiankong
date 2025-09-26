#!/usr/bin/env python3
"""
GitHub Actions构建脚本
用于在不同平台上构建PD-Signal应用程序
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def log_info(message):
    """输出信息日志"""
    print(f"ℹ️  {message}")

def log_error(message):
    """输出错误日志"""
    print(f"❌ {message}")

def log_success(message):
    """输出成功日志"""
    print(f"✅ {message}")

def run_command(cmd, description=""):
    """运行命令并处理错误"""
    try:
        log_info(f"运行命令: {cmd}")
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if description:
            log_success(description)
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"命令失败: {cmd}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def check_dependencies():
    """检查依赖项"""
    log_info("检查依赖项...")
    
    # 检查Python版本
    python_version = sys.version_info
    log_info(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        log_error("需要Python 3.8或更高版本")
        return False
    
    # 检查必要的包
    required_packages = ['flet', 'requests', 'plyer', 'pyinstaller']
    for package in required_packages:
        try:
            __import__(package)
            log_success(f"包 {package} 已安装")
        except ImportError:
            log_error(f"包 {package} 未安装")
            return False
    
    return True

def clean_build_dirs():
    """清理构建目录"""
    log_info("清理构建目录...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            log_success(f"已删除目录: {dir_name}")
    
    # 清理.spec文件
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        log_success(f"已删除文件: {spec_file}")

def build_executable():
    """构建可执行文件"""
    log_info("开始构建可执行文件...")
    
    # 获取当前平台
    current_platform = platform.system().lower()
    log_info(f"当前平台: {current_platform}")
    
    # 构建PyInstaller命令
    cmd_parts = [
        "pyinstaller",
        "--onefile",  # 单文件模式
        "--windowed",  # 无控制台窗口
        "--name", "PD-Signal",
        "--distpath", "dist/PD-Signal",
        "--workpath", "build",
        "--specpath", ".",
        "main.py"
    ]
    
    # 添加平台特定的选项
    if current_platform == "windows":
        cmd_parts.extend([
            "--add-data", "usersetting.json;.",
            "--add-data", "sql;sql"
        ])
    else:  # macOS和Linux
        cmd_parts.extend([
            "--add-data", "usersetting.json:.",
            "--add-data", "sql:sql"
        ])
    
    cmd = " ".join(cmd_parts)
    
    if not run_command(cmd, "PyInstaller构建完成"):
        return False
    
    # 检查构建结果
    if current_platform == "windows":
        exe_path = "dist/PD-Signal/PD-Signal.exe"
    else:
        exe_path = "dist/PD-Signal/PD-Signal"
    
    if not os.path.exists(exe_path):
        log_error(f"可执行文件未找到: {exe_path}")
        return False
    
    log_success(f"可执行文件已创建: {exe_path}")
    
    # 显示文件大小
    file_size = os.path.getsize(exe_path)
    log_info(f"文件大小: {file_size / (1024*1024):.2f} MB")
    
    return True

def create_additional_files():
    """创建额外的文件"""
    log_info("创建额外文件...")
    
    # 创建启动脚本
    if platform.system().lower() == "windows":
        bat_content = """@echo off
echo 启动PD-Signal...
PD-Signal.exe
pause
"""
        with open("dist/启动PD-Signal.bat", "w", encoding="utf-8") as f:
            f.write(bat_content)
        log_success("已创建启动脚本: 启动PD-Signal.bat")
        
        # 创建调试脚本
        debug_content = """@echo off
echo 调试模式启动PD-Signal...
PD-Signal.exe --debug
pause
"""
        with open("dist/调试模式.bat", "w", encoding="utf-8") as f:
            f.write(debug_content)
        log_success("已创建调试脚本: 调试模式.bat")
    
    # 创建使用说明
    readme_content = """# PD-Signal 使用说明

## 功能特点
- 支持多主播同时监控
- 实时开播/下播通知
- Windows系统通知
- 数据持久化存储
- 现代化GUI界面
- 配置自动保存

## 使用方法
1. 运行 PD-Signal.exe 启动程序
2. 在界面中添加要监控的主播ID
3. 设置监控间隔时间
4. 点击"开始监控"按钮

## 注意事项
- 首次使用需要设置Cookie
- 建议设置合理的监控间隔（建议30秒以上）
- 程序会自动保存配置

## 故障排除
如果程序无法正常运行，请尝试：
1. 检查网络连接
2. 更新Cookie
3. 使用调试模式查看详细错误信息
"""
    
    with open("dist/使用说明.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    log_success("已创建使用说明: 使用说明.txt")
    
    return True

def main():
    """主函数"""
    log_info("开始GitHub Actions构建流程...")
    
    try:
        # 检查依赖项
        if not check_dependencies():
            log_error("依赖项检查失败")
            sys.exit(1)
        
        # 清理构建目录
        clean_build_dirs()
        
        # 构建可执行文件
        if not build_executable():
            log_error("构建可执行文件失败")
            sys.exit(1)
        
        # 创建额外文件
        if not create_additional_files():
            log_error("创建额外文件失败")
            sys.exit(1)
        
        log_success("构建流程完成！")
        
    except Exception as e:
        log_error(f"构建过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
