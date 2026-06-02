@echo off
setlocal enabledelayedexpansion

echo =============================================
echo  Instalasi Parkir Video Recorder Service
echo =============================================
echo.

:: Cek Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Harap jalankan sebagai Administrator!
    pause
    exit /b 1
)

set "SERVICE_NAME=ParkirVideoRecorder"
set "PORT=5050"

:: Cek argumen port
if not "%1"=="" set "PORT=%1"

set "SCRIPT_DIR=%~dp0"
set "PYTHON_DIR=%LOCALAPPDATA%\Programs\Python\Python313"
set "VENV_DIR=%SCRIPT_DIR%venv"

echo [1/4] Membuat virtual environment...
if exist "%VENV_DIR%" (
    echo Virtual environment sudah ada, melewati...
) else (
    "%PYTHON_DIR%\python.exe" -m venv "%VENV_DIR%"
    if !errorlevel! neq 0 (
        echo [!] Gagal membuat virtual environment
        pause
        exit /b 1
    )
)

echo [2/4] Menginstall dependencies...
"%VENV_DIR%\Scripts\pip.exe" install -r "%SCRIPT_DIR%requirements.txt"
if !errorlevel! neq 0 (
    echo [!] Gagal menginstall dependencies
    pause
    exit /b 1
)

echo [3/4] Menginstall NSSM...
where nssm >nul 2>&1
if !errorlevel! neq 0 (
    echo Mengunduh NSSM...
    powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile '%TEMP%\nssm.zip'"
    powershell -Command "Expand-Archive -Path '%TEMP%\nssm.zip' -DestinationPath '%TEMP%\nssm' -Force"
    copy "%TEMP%\nssm\nssm-2.24\win64\nssm.exe" "%SYSTEMROOT%\system32\nssm.exe" /Y
) else (
    echo NSSM sudah terinstall.
)

echo [4/4] Membuat Windows Service...
nssm stop "%SERVICE_NAME%" >nul 2>&1
nssm remove "%SERVICE_NAME%" confirm >nul 2>&1

nssm install "%SERVICE_NAME%" "%VENV_DIR%\Scripts\python.exe"
nssm set "%SERVICE_NAME%" AppParameters "%SCRIPT_DIR%src\recording_service.py"
nssm set "%SERVICE_NAME%" AppDirectory "%SCRIPT_DIR%"
nssm set "%SERVICE_NAME%" DisplayName "Parkir Video Recorder"
nssm set "%SERVICE_NAME%" Description "Merekam video dari RTSP camera untuk SMARTPARK"
nssm set "%SERVICE_NAME%" Start SERVICE_AUTO_START
nssm set "%SERVICE_NAME%" AppStdout "%SCRIPT_DIR%logs\service.log"
nssm set "%SERVICE_NAME%" AppStderr "%SCRIPT_DIR%logs\error.log"
nssm set "%SERVICE_NAME%" AppEnvironmentExtra "PORT=%PORT%"

nssm start "%SERVICE_NAME%"

echo.
echo =============================================
echo  Service "%SERVICE_NAME%" berhasil diinstall
echo  Port: %PORT%
echo  Logs: %SCRIPT_DIR%logs\
echo =============================================
pause
