@echo off
setlocal enabledelayedexpansion

:: Set maximum retry count
set MAX_RETRIES=3
set RETRY_COUNT=0

:retry
set /a RETRY_COUNT+=1

echo Attempt !RETRY_COUNT! of %MAX_RETRIES%


:: Kill any existing processes
taskkill /F /IM "qemu-system-x86_64.exe" /T >nul 2>&1
taskkill /F /IM "emulator.exe" /T >nul 2>&1
taskkill /F /IM "adb.exe" /T >nul 2>&1
taskkill /F /IM "node.exe" /T >nul 2>&1

:: Wait for processes to end
timeout /t 5 /nobreak >nul

:: Start Appium first
start cmd.exe /c "call conda activate ds && appium"

:: Wait for Appium to fully start
timeout /t 15 /nobreak >nul

:: Now run the script
python "demo.py"

:: Check for errors
if errorlevel 1 (
    echo Script failed on attempt !RETRY_COUNT!
    if !RETRY_COUNT! lss %MAX_RETRIES% (
        echo Retrying in 30 seconds...
        timeout /t 30 /nobreak
        goto :retry
    ) else (
        echo Maximum retry attempts reached
        echo Check booking_log.txt for details
        pause
        exit /b 1
    )
)

echo Script completed successfully
pause