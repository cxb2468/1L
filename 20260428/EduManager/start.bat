@echo off
chcp 65001 >nul
echo ========================================
echo     校务管理系统 - Python版本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [1/3] 检查依赖包...
pip list | findstr fastapi >nul
if errorlevel 1 (
    echo [提示] 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖包安装失败
        pause
        exit /b 1
    )
) else (
    echo [完成] 依赖包已安装
)

echo.
echo [2/3] 初始化数据库...
python init_db.py
if errorlevel 1 (
    echo [错误] 数据库初始化失败
    pause
    exit /b 1
)

echo.
echo [3/3] 启动服务器...
echo.
echo ========================================
echo 服务器即将启动
echo 访问地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.

python main.py

pause
