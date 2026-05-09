@echo off
chcp 65001 >nul
echo ============================================================
echo           农历生日转换器 - 打包工具
echo ============================================================
echo.

REM 设置变量
set PACKAGE_NAME=农历生日转换器Web版
set VERSION=1.0
set DATE=%date:~0,4%%date:~5,2%%date:~8,2%
set ZIP_FILE=%PACKAGE_NAME%_v%VERSION%_%DATE%.zip

echo 正在打包文件...
echo.

REM 创建临时目录
if exist "deploy_temp" rmdir /s /q "deploy_temp"
mkdir deploy_temp
mkdir deploy_temp\templates

REM 复制必要文件
echo [1/6] 复制核心文件...
copy app.py deploy_temp\ >nul
copy birthday_converter.py deploy_temp\ >nul
copy requirements_web.txt deploy_temp\ >nul

echo [2/6] 复制模板文件...
copy templates\index.html deploy_temp\templates\ >nul

echo [3/6] 复制启动脚本...
copy install_and_run.bat deploy_temp\ >nul
copy 启动Web服务.bat deploy_temp\ >nul

echo [4/6] 复制文档...
copy README_Web版.md deploy_temp\ >nul
copy 快速开始.md deploy_temp\ >nul
copy 部署指南.md deploy_temp\ >nul
copy 部署速查卡.md deploy_temp\ >nul

echo [5/6] 创建README...
(
echo # 农历生日转换器 Web版 v%VERSION%
echo.
echo ## 快速开始
echo.
echo ### Windows用户
echo 双击运行 `install_and_run.bat` 即可自动安装并启动
echo.
echo ### 手动安装
echo ```bash
echo pip install -r requirements_web.txt
echo python app.py
echo ```
echo.
echo ### 访问地址
echo - 本机: http://localhost:5001
echo - 局域网: http://你的IP:5001
echo.
echo ## 文档
echo - 快速开始.md - 基础使用
echo - 部署指南.md - 详细部署说明
echo - 部署速查卡.md - 常用命令速查
echo.
echo © 2026 农历生日转换器
) > deploy_temp\README.txt

echo [6/6] 压缩文件...

REM 检查是否有7z
where 7z >nul 2>&1
if %errorlevel% equ 0 (
    7z a -tzip "%ZIP_FILE%" ".\deploy_temp\*" -mx=9
) else (
    REM 使用PowerShell压缩
    powershell -Command "Compress-Archive -Path 'deploy_temp\*' -DestinationPath '%ZIP_FILE%' -Force"
)

REM 清理临时目录
rmdir /s /q deploy_temp

echo.
echo ============================================================
echo 打包完成！
echo.
echo 文件名: %ZIP_FILE%
echo 位置: %CD%\%ZIP_FILE%
echo.
echo 将此文件复制到目标电脑，解压后运行:
echo install_and_run.bat
echo ============================================================
echo.

pause
