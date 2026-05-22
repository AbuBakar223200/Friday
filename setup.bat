@echo off
setlocal

cd /d "%~dp0"

echo.
echo Friday student setup
echo ====================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found.
    echo Install Python 3.10 or newer from https://www.python.org/downloads/windows/
    echo Make sure to check "Add python.exe to PATH" during installation.
    pause
    exit /b 1
)

python --version
if errorlevel 1 (
    echo Python is installed, but it did not run correctly from this terminal.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Could not create the virtual environment.
        pause
        exit /b 1
    )
)

echo.
echo Upgrading pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
    echo pip upgrade failed. Continuing to dependency install so you can see the exact error.
)

echo.
echo Installing Friday dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Dependency installation failed.
    echo If PyAudio failed, install a matching wheel or try:
    echo   ".venv\Scripts\python.exe" -m pip install pipwin
    echo   ".venv\Scripts\python.exe" -m pipwin install pyaudio
    pause
    exit /b 1
)

if not exist ".env" (
    echo.
    echo Creating .env from .env.example...
    copy ".env.example" ".env" >nul
    echo Open .env and paste one provider key, such as GEMINI_API_KEY.
) else (
    echo.
    echo .env already exists. Keeping your existing settings.
)

echo.
echo Running setup checker...
".venv\Scripts\python.exe" check_setup.py
set "CHECK_RESULT=%ERRORLEVEL%"
if not "%CHECK_RESULT%"=="0" (
    echo.
    echo Setup checker found blocking issues. Fix them and run setup.bat again.
    pause
    exit /b %CHECK_RESULT%
)

echo.
echo Setup finished. If the checker shows missing items, fix those and run setup.bat again.
pause
