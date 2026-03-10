@echo off
chcp 65001 >nul

echo ========================================
echo  Route294 初回セットアップ
echo ========================================
echo.

set APP_DIR=%~dp0
set PYTHON_EXE=%APP_DIR%python\python.exe
set ROUTE_DIR=%APP_DIR%route

cd /d "%ROUTE_DIR%"

echo データベースを初期化しています...
"%PYTHON_EXE%" manage.py migrate --run-syncdb

echo.
echo 管理者アカウントを作成します。
echo （ユーザー名、メールアドレス、パスワードを入力してください）
echo.
"%PYTHON_EXE%" manage.py createsuperuser

echo.
echo ========================================
echo  セットアップ完了!
echo  launcher.bat またはデスクトップショートカットで起動できます。
echo ========================================
pause
