@echo off
chcp 65001 >nul
echo 启动PD Signal...
echo ==================

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python
    echo 请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖是否安装
python -c "import flet" >nul 2>&1
if %errorlevel% neq 0 (
    echo 检测到缺少依赖，正在安装...
    call install_dependencies.bat
)

echo 正在启动程序...
python main.py

if %errorlevel% neq 0 (
    echo 程序异常退出，错误代码: %errorlevel%
    pause
)
