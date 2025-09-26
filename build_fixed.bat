@echo off
chcp 65001 >nul
echo ========================================
echo    PD Signal 修复版构建脚本
echo    解决无限循环创建进程问题
echo ========================================
echo.

echo 第1步: 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python
    echo 请先安装Python 3.8或更高版本
    pause
    exit /b 1
)
echo ✅ Python环境检查通过
echo.

echo 第2步: 安装/更新依赖...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo ✅ 依赖安装完成
echo.

echo 第3步: 清理旧的构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"
echo ✅ 清理完成
echo.

echo 第4步: 构建可执行文件（修复版）...
python build_fixed.py
if %errorlevel% neq 0 (
    echo ❌ 构建失败
    pause
    exit /b 1
)
echo ✅ 构建完成
echo.

echo 第5步: 创建发布包...
if not exist "release" mkdir "release"
if exist "release\PD-Signal-Fixed" rmdir /s /q "release\PD-Signal-Fixed"
mkdir "release\PD-Signal-Fixed"

REM 复制可执行文件
copy "dist\PD-Signal.exe" "release\PD-Signal-Fixed\"
copy "dist\启动PD-Signal.bat" "release\PD-Signal-Fixed\"
copy "dist\使用说明.txt" "release\PD-Signal-Fixed\"

REM 复制源码（可选）
mkdir "release\PD-Signal-Fixed\source"
copy "*.py" "release\PD-Signal-Fixed\source\"
copy "requirements.txt" "release\PD-Signal-Fixed\source\"
copy "README_CN.md" "release\PD-Signal-Fixed\source\"

echo ✅ 发布包创建完成
echo.

echo ========================================
echo 🎉 修复版构建完成！
echo ========================================
echo 📁 发布目录: release\PD-Signal-Fixed\
echo 📋 包含文件:
dir "release\PD-Signal-Fixed\" /b
echo.
echo 💡 使用提示:
echo    1. 运行 PD-Signal.exe 启动程序
echo    2. 使用 启动PD-Signal.bat 可查看控制台输出
echo    3. 阅读 使用说明.txt 了解详细用法
echo    4. source目录包含完整源代码
echo    5. 此版本已修复无限循环创建进程的问题
echo.
echo 🔧 修复内容:
echo    - 添加了完整的依赖包收集
echo    - 优化了隐藏导入配置
echo    - 排除了不必要的模块
echo    - 禁用了UPX压缩避免兼容性问题
echo.
echo 按任意键退出...
pause >nul
