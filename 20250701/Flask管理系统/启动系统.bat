@echo off
chcp 65001 >nul
title Flask管理系统
echo ========================================
echo            Flask管理系统
echo ========================================
echo.
echo 正在启动系统，请稍候...
echo.
echo 启动后请在浏览器中访问以下地址之一：
echo   - http://localhost:5000
echo   - http://127.0.0.1:5000
echo.
echo 如需修改端口，请编辑 config.py 文件中的 PORT 值
echo.
echo 按 Ctrl+C 可以停止服务
echo.
Flask管理系统.exe
pause
