@echo off
chcp 65001 >nul
echo ========================================
echo    PD Signal 改进版构建脚本
echo    解决无法正确打开的问题
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

echo 第4步: 构建可执行文件（改进版）...
python build_improved.py
if %errorlevel% neq 0 (
    echo ❌ 构建失败
    pause
    exit /b 1
)
echo ✅ 构建完成
echo.

echo 第5步: 创建发布包...
if not exist "release" mkdir "release"
if exist "release\PD-Signal-Improved" rmdir /s /q "release\PD-Signal-Improved"
mkdir "release\PD-Signal-Improved"

REM 复制可执行文件
if exist "dist\PD-Signal\PD-Signal.exe" (
    copy "dist\PD-Signal\PD-Signal.exe" "release\PD-Signal-Improved\"
    echo ✅ 复制主程序
) else (
    echo ❌ 未找到主程序文件
)

if exist "dist\启动PD-Signal.bat" (
    copy "dist\启动PD-Signal.bat" "release\PD-Signal-Improved\"
    echo ✅ 复制启动脚本
)

if exist "dist\调试模式.bat" (
    copy "dist\调试模式.bat" "release\PD-Signal-Improved\"
    echo ✅ 复制调试脚本
)

if exist "dist\使用说明.txt" (
    copy "dist\使用说明.txt" "release\PD-Signal-Improved\"
    echo ✅ 复制使用说明
)

REM 复制依赖文件
if exist "dist\PD-Signal" (
    xcopy "dist\PD-Signal\*" "release\PD-Signal-Improved\" /E /I /Y
    echo ✅ 复制依赖文件
)

REM 复制源码（可选）
mkdir "release\PD-Signal-Improved\source"
copy "*.py" "release\PD-Signal-Improved\source\"
copy "requirements.txt" "release\PD-Signal-Improved\source\"
copy "README_CN.md" "release\PD-Signal-Improved\source\"

echo ✅ 发布包创建完成
echo.

echo ========================================
echo 🎉 改进版构建完成！
echo ========================================
echo 📁 发布目录: release\PD-Signal-Improved\
echo 📋 包含文件:
dir "release\PD-Signal-Improved\" /b
echo.
echo 💡 使用提示:
echo    1. 运行 PD-Signal.exe 启动程序
echo    2. 使用 启动PD-Signal.bat 可查看控制台输出
echo    3. 使用 调试模式.bat 可查看详细错误信息
echo    4. 阅读 使用说明.txt 了解详细用法
echo    5. source目录包含完整源代码
echo.
echo 🔧 改进内容:
echo    - 修复了单实例检查问题
echo    - 优化了路径处理
echo    - 完善了依赖收集
echo    - 添加了调试模式
echo    - 改进了错误处理
echo.
echo 按任意键退出...
pause >nul
