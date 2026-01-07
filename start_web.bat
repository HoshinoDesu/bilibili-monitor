@echo off
chcp 65001 >nul
echo ====================================
echo Bilibili视频热度监视器 - Web服务
echo ====================================
echo.

echo 启动Flask Web服务...
echo.
echo 服务启动后请访问: http://localhost:5000
echo 按 Ctrl+C 可停止服务
echo.

python app.py

pause
