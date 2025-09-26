# 本地构建脚本 - build_local.bat
@echo off
chcp 65001 >nul
echo 开始本地构建 PDSignal...

REM 检查Python是否安装
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.11
    pause
    exit /b 1
)

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt

REM 清理之前的构建
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM 使用PyInstaller构建
echo 开始构建...
pyinstaller --name="PDSignal" ^
  --windowed ^
  --onedir ^
  --icon="pandatv.ico" ^
  --distpath="dist" ^
  --workpath="build" ^
  --specpath="." ^
  --add-data="sql;sql" ^
  --add-data="usersetting.json;." ^
  --hidden-import="flet" ^
  --hidden-import="plyer" ^
  --hidden-import="requests" ^
  --hidden-import="certifi" ^
  --hidden-import="urllib3" ^
  --hidden-import="charset_normalizer" ^
  --hidden-import="idna" ^
  main.py

if %errorlevel% equ 0 (
    echo 构建成功！可执行文件位于: dist\PDSignal\PDSignal.exe
    echo 按任意键打开构建目录...
    pause
    explorer dist\PDSignal
) else (
    echo 构建失败！
    pause
)
