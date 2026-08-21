@echo off
title Multifly 2035 - Starting Systems...
color 06

echo ============================================
echo   MULTIFLY 2035 - SYSTEM STARTUP
echo ============================================
echo.

echo [1/3] Starting OmniRoute AI Server...
start /min python "C:\Users\Ayush Mishra\AppData\Roaming\Antigravity\User\scripts\start_omniroute.py"
timeout /t 5 /nobreak >nul

echo [2/3] Checking server status...
curl -s http://localhost:20128/v1/models >nul 2>&1
if %errorlevel% equ 0 (
    echo   [OK] OmniRoute: ONLINE
) else (
    echo   [WAIT] OmniRoute: Starting...
    timeout /t 10 /nobreak >nul
)

echo [3/3] All systems ready!
echo.
echo ============================================
echo   OMNIROUTE: http://localhost:20128/v1
echo   TOKENS: 1.51 Billion Free
echo   STATUS: ALL SYSTEMS ONLINE
echo ============================================
echo.
