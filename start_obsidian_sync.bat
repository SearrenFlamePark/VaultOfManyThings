@echo off
echo 🔥 Starting Obsidian to ChatGPT Auto-Sync
echo ==========================================
echo.
echo This will sync your Obsidian vaults to ChatGPT:
echo - C:\vaultclean\vaultofmanythings
echo - C:\users\delph\Onedrive\searrenobsidianvault
echo.
echo Press Ctrl+C to stop anytime
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.7+ first.
    echo Download from: https://python.org/downloads
    pause
    exit /b 1
)

REM Install required packages
echo 🔧 Installing required packages...
pip install requests watchdog >nul 2>&1

REM Run the sync system
echo ✅ Starting sync...
python windows_obsidian_sync.py

pause