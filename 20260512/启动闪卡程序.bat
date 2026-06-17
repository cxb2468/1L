@echo off
chcp 65001 >nul
echo ========================================
echo    📚 正在启动英语闪卡背诵程序...
echo ========================================
echo.
cd /d "%~dp0"
python english_flashcard_v2.py
if errorlevel 1 (
    echo.
    echo ❌ 程序运行出错！
    echo 请确保已安装依赖：pip install PyQt5 gTTS
    pause
)
