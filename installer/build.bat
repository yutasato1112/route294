@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ========================================
REM  Route294 Installer Build Script
REM  Windows 11 上で実行してください
REM ========================================

set PYTHON_VERSION=3.12.7
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-embed-amd64.zip
set BUILD_DIR=%~dp0build
set PROJECT_ROOT=%~dp0..

echo ========================================
echo   Route294 Installer Build Script
echo   Python %PYTHON_VERSION% Embedded
echo ========================================
echo.

REM ----------------------------------------
REM 1. Clean previous build
REM ----------------------------------------
if exist "%BUILD_DIR%" (
    echo 以前のビルドを削除しています...
    rmdir /s /q "%BUILD_DIR%"
)
mkdir "%BUILD_DIR%"
mkdir "%BUILD_DIR%\python"
mkdir "%BUILD_DIR%\route"
mkdir "%BUILD_DIR%\route\logs"
mkdir "%BUILD_DIR%\route\media"

REM ----------------------------------------
REM 2. Download Python Embedded
REM ----------------------------------------
echo.
echo [1/5] Python %PYTHON_VERSION% Embedded をダウンロード中...
curl -L -o "%BUILD_DIR%\python-embed.zip" %PYTHON_URL%
if errorlevel 1 (
    echo ERROR: Python のダウンロードに失敗しました。
    echo URL: %PYTHON_URL%
    pause
    exit /b 1
)

echo 展開中...
tar -xf "%BUILD_DIR%\python-embed.zip" -C "%BUILD_DIR%\python"
del "%BUILD_DIR%\python-embed.zip"

REM ----------------------------------------
REM 3. Enable pip in embedded Python
REM    python312._pth の import site を有効化
REM ----------------------------------------
echo.
echo [2/5] pip を有効化しています...

REM Find and modify the ._pth file
for %%f in ("%BUILD_DIR%\python\python*._pth") do (
    echo python312.zip> "%%f"
    echo .>> "%%f"
    echo ..\\route>> "%%f"
    echo import site>> "%%f"
)

REM Download and install pip
curl -L -o "%BUILD_DIR%\get-pip.py" https://bootstrap.pypa.io/get-pip.py
if errorlevel 1 (
    echo ERROR: get-pip.py のダウンロードに失敗しました。
    pause
    exit /b 1
)
"%BUILD_DIR%\python\python.exe" "%BUILD_DIR%\get-pip.py" --no-warn-script-location
del "%BUILD_DIR%\get-pip.py"

REM ----------------------------------------
REM 4. Install dependencies
REM ----------------------------------------
echo.
echo [3/5] 依存パッケージをインストール中...
echo （google-cloud-translate 等の大きいパッケージがあるため数分かかります）
"%BUILD_DIR%\python\python.exe" -m pip install -r "%PROJECT_ROOT%\requirements.txt" --no-warn-script-location
if errorlevel 1 (
    echo ERROR: 依存パッケージのインストールに失敗しました。
    pause
    exit /b 1
)

REM pip cache を削除して容量削減
"%BUILD_DIR%\python\python.exe" -m pip cache purge 2>nul

REM ----------------------------------------
REM 5. Copy project files
REM ----------------------------------------
echo.
echo [4/5] プロジェクトファイルをコピー中...

REM Copy route/ project (excluding unnecessary files)
robocopy "%PROJECT_ROOT%\route" "%BUILD_DIR%\route" /E /XD __pycache__ .git media logs migrations >nul
REM migrations は必要なのでコピーし直す
robocopy "%PROJECT_ROOT%\route\cleaning\migrations" "%BUILD_DIR%\route\cleaning\migrations" /E /XD __pycache__ >nul

REM Copy launcher scripts
copy "%~dp0scripts\launcher.bat" "%BUILD_DIR%\" >nul
copy "%~dp0scripts\stop.bat" "%BUILD_DIR%\" >nul
copy "%~dp0scripts\first_setup.bat" "%BUILD_DIR%\" >nul

REM Create empty directories
if not exist "%BUILD_DIR%\route\logs" mkdir "%BUILD_DIR%\route\logs"
if not exist "%BUILD_DIR%\route\media" mkdir "%BUILD_DIR%\route\media"

REM Remove sensitive files if present
del "%BUILD_DIR%\route\static\email.json" 2>nul
del "%BUILD_DIR%\route\static\openai.json" 2>nul
del "%BUILD_DIR%\route\db.sqlite3" 2>nul

REM ----------------------------------------
REM 6. Summary
REM ----------------------------------------
echo.
echo [5/5] ビルド完了!
echo.
echo ========================================
echo   ビルドディレクトリ: %BUILD_DIR%
echo.
echo   次のステップ:
echo   1. Inno Setup をインストール (https://jrsoftware.org/isinfo.php)
echo   2. route294.iss を Inno Setup で開く
echo   3. [Build] → [Compile] でインストーラを生成
echo ========================================
echo.
pause
