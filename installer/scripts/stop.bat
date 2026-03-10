@echo off
chcp 65001 >nul
echo Route294 サーバーを停止しています...

REM Find and kill the Django server process
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo サーバーを停止しました。
timeout /t 2 /nobreak >nul
