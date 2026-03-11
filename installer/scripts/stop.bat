@echo off
chcp 65001 >nul
echo Route294 サーバーを停止しています...

REM Find and kill Django server processes on ports 8000-8099
for /L %%p in (8000,1,8099) do (
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%%p" ^| findstr "LISTENING"') do (
        taskkill /f /pid %%a >nul 2>&1
    )
)

echo サーバーを停止しました。
timeout /t 2 /nobreak >nul
