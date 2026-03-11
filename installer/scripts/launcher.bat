@echo off
chcp 65001 >nul
title Route294 - ホテル清掃指示書作成システム

echo.
echo  ╔════════════════════════════════════════╗
echo  ║  Route294                              ║
echo  ║  ホテル清掃指示書作成システム          ║
echo  ╚════════════════════════════════════════╝
echo.

set APP_DIR=%~dp0
set PYTHON_EXE=%APP_DIR%python\python.exe
set ROUTE_DIR=%APP_DIR%route

REM Check if Python exists
if not exist "%PYTHON_EXE%" (
    echo ERROR: Python が見つかりません: %PYTHON_EXE%
    echo インストールが壊れている可能性があります。再インストールしてください。
    pause
    exit /b 1
)

REM Create logs/media directories if missing
if not exist "%ROUTE_DIR%\logs" mkdir "%ROUTE_DIR%\logs"
if not exist "%ROUTE_DIR%\media" mkdir "%ROUTE_DIR%\media"

REM Create default email.json if missing
if not exist "%ROUTE_DIR%\static\email.json" (
    echo {"address": "", "password": "", "developer_address": ""} > "%ROUTE_DIR%\static\email.json"
)

REM Run initial setup (migrations) if DB doesn't exist
if not exist "%ROUTE_DIR%\db.sqlite3" (
    echo 初回セットアップを実行しています...
    cd /d "%ROUTE_DIR%"
    "%PYTHON_EXE%" manage.py migrate --run-syncdb >nul 2>&1
    echo セットアップ完了。
    echo.
)

REM Pre-check: verify Django can be imported
"%PYTHON_EXE%" -c "import django" 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Django が正しくインストールされていません。
    echo 再インストールしてください。
    echo.
    pause
    exit /b 1
)

REM Find an available port starting from 8000
set PORT=8000

:find_port
netstat -an | findstr ":%PORT% .*LISTENING" >nul 2>&1
if %errorlevel%==0 (
    echo ポート %PORT% は使用中です。次のポートを試します...
    set /a PORT+=1
    if %PORT% GEQ 8100 (
        echo ERROR: 利用可能なポートが見つかりませんでした（8000-8099）。
        pause
        exit /b 1
    )
    goto find_port
)

REM Start Django server
echo サーバーを起動しています...（ポート: %PORT%）
echo.
echo  ブラウザで http://localhost:%PORT%/ が開きます。
echo  このウィンドウを閉じるとサーバーが停止します。
echo.
echo  ────────────────────────────────────────
echo.

cd /d "%ROUTE_DIR%"

REM Open browser after 2 second delay
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:%PORT%/"

REM Start Django development server (blocks until Ctrl+C or window close)
"%PYTHON_EXE%" manage.py runserver localhost:%PORT% 2>&1

if errorlevel 1 (
    echo.
    echo ════════════════════════════════════════
    echo  ERROR: サーバーの起動に失敗しました。
    echo  上記のエラーメッセージを確認してください。
    echo ════════════════════════════════════════
    echo.
    pause
    exit /b 1
)

echo.
echo サーバーが停止しました。
pause
