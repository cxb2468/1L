@echo off
chcp 65001 >nul
echo ============================================================
echo           农历生日转换器 - Web版 启动程序
echo ============================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python
    pause
    exit /b 1
)

echo [1/3] 检查依赖包...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装Flask及相关依赖...
    pip install -r requirements_web.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
) else (
    echo [成功] 依赖包已安装
)

echo.
echo [2/3] 创建必要目录...
if not exist uploads mkdir uploads
if not exist downloads mkdir downloads
if not exist templates mkdir templates
echo [成功] 目录创建完成

echo.
echo [3/3] 启动Web服务器...
echo.
echo ============================================================
echo  服务器即将启动
echo  访问地址: http://localhost:5000
echo  局域网访问: http://你的IP地址:5000
echo  按 Ctrl+C 停止服务器
echo ============================================================
echo.

python app.py

pause
