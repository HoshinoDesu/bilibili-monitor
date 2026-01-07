@echo off
chcp 65001 >nul
echo ====================================
echo Bilibili视频热度监视器 - 启动脚本
echo ====================================
echo.

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)
echo ✓ Python已安装

echo.
echo [2/3] 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo ✗ 依赖安装失败
    pause
    exit /b 1
)
echo ✓ 依赖安装成功

echo.
echo [3/3] 启动监控程序...
echo.
echo 提示：
echo   - 监控程序将在后台定时抓取数据
echo   - 请在另一个终端运行 start_web.bat 启动Web界面
echo   - 按 Ctrl+C 可停止监控
echo.
python monitor.py

pause
