@echo off
chcp 65001 >nul
title Flask管理系统初始化
echo ========================================
echo         Flask管理系统初始化
echo ========================================
echo.
echo 正在初始化系统...
echo.

REM 使用打包后的可执行文件进行初始化
Flask管理系统.exe --init

echo.
echo 初始化完成！
echo 请使用以下账户登录：
echo 用户名: admin
echo 密码: admin123
echo.
echo 现在可以双击"启动系统.bat"启动应用了
echo.
pause
