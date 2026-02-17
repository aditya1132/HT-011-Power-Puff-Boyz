@echo off
echo ========================================
echo  AI Mental Health Companion - Demo
echo ========================================
echo.
echo Starting your mental health companion demo...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "backend\demo_server.py" (
    echo ERROR: Please run this script from the ai-mental-health-companion directory
    echo Current directory: %cd%
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

REM Start the backend server
echo 🚀 Starting backend server...
echo.
echo 📡 API Documentation will be available at: http://localhost:8000/docs
echo 💬 Demo Interface will be available at: http://localhost:8000/demo
echo.
echo ⚠️  Important Safety Notice:
echo    This is a demo tool for emotional support, NOT a replacement for professional care
echo    Crisis Support: National Suicide Prevention Lifeline 988
echo.
echo 🌱 Starting server... (Press Ctrl+C to stop)
echo.

REM Change to backend directory and start server
cd backend
python demo_server.py

REM If server stops, return to original directory
cd ..
echo.
echo Server stopped.
pause
