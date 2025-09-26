@echo off
chcp 65001 >nul
echo 正在安装PD Signal依赖包...
echo ================================

echo 检查Python版本...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

echo.
echo 升级pip...
python -m pip install --upgrade pip

echo.
echo 安装基础依赖...
python -m pip install -r requirements.txt

echo.
echo 安装打包工具...
python -m pip install pyinstaller

echo.
echo ================================
echo 依赖安装完成！
echo 现在可以运行以下命令：
echo   python main.py          - 直接运行程序
echo   python build.py         - 构建可执行文件
echo ================================
pause
