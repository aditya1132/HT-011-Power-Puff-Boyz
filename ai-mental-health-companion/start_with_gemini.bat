@echo off
REM =============================================================================
REM AI Mental Health Companion - Quick Start with Gemini AI
REM =============================================================================
REM This script starts the complete system with Gemini AI integration
REM Make sure you have configured your .env file with GEMINI_API_KEY

echo ===============================================================
echo 🤖 AI Mental Health Companion - Starting with Gemini AI
echo ===============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.9+ and try again
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js 18+ and try again
    pause
    exit /b 1
)

echo ✅ Python and Node.js found

REM Step 1: Test Gemini API connection
echo.
echo 🔍 Step 1: Testing Gemini API connection...
echo -----------------------------------------------
python test_gemini_connection.py
if errorlevel 1 (
    echo.
    echo ❌ Gemini API test failed!
    echo Please check your API key configuration in backend\.env
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Gemini API connection successful!

REM Step 2: Install backend dependencies
echo.
echo 📦 Step 2: Installing backend dependencies...
echo -----------------------------------------------
cd backend
if not exist requirements.txt (
    echo ❌ requirements.txt not found in backend directory
    pause
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install backend dependencies
    pause
    exit /b 1
)

echo ✅ Backend dependencies installed

REM Step 3: Initialize database
echo.
echo 🗄️ Step 3: Initializing database...
echo -----------------------------------------------
if not exist data mkdir data
python -c "
try:
    from app.database.database import Base, engine
    Base.metadata.create_all(bind=engine)
    print('✅ Database initialized successfully!')
except Exception as e:
    print(f'❌ Database initialization failed: {e}')
    exit(1)
"
if errorlevel 1 (
    echo Database initialization failed
    pause
    exit /b 1
)

REM Step 4: Start backend server
echo.
echo 🚀 Step 4: Starting backend server with Gemini AI...
echo -----------------------------------------------
echo Backend will start at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo AI Health Check: http://localhost:8000/health/ai
echo.
echo Starting server in 3 seconds...
timeout /t 3 >nul

REM Start backend in a new window
start "AI Mental Health Backend" cmd /c "python -m app.main & pause"

REM Wait a moment for backend to start
timeout /t 5 >nul

REM Step 5: Test backend health
echo.
echo 🏥 Step 5: Testing backend health...
echo -----------------------------------------------
python -c "
import requests
import json
try:
    response = requests.get('http://localhost:8000/health', timeout=10)
    if response.status_code == 200:
        print('✅ Backend server is healthy!')

        # Test AI health
        ai_response = requests.get('http://localhost:8000/health/ai', timeout=10)
        if ai_response.status_code == 200:
            ai_data = ai_response.json()
            print(f'✅ AI services status: {ai_data.get(\"status\", \"unknown\")}')
            if ai_data.get('gemini_enabled'):
                print('✅ Gemini AI is enabled and ready!')
        else:
            print('⚠️ AI health check failed, but server is running')
    else:
        print('❌ Backend server health check failed')
        exit(1)
except Exception as e:
    print(f'❌ Cannot connect to backend server: {e}')
    print('Please check if the server started correctly')
    exit(1)
"
if errorlevel 1 (
    echo.
    echo ❌ Backend server is not responding properly
    echo Please check the backend server window for errors
    pause
    exit /b 1
)

cd ..

REM Step 6: Install frontend dependencies
echo.
echo 📦 Step 6: Installing frontend dependencies...
echo -----------------------------------------------
cd frontend
if not exist package.json (
    echo ❌ package.json not found in frontend directory
    pause
    exit /b 1
)

call npm install
if errorlevel 1 (
    echo ❌ Failed to install frontend dependencies
    pause
    exit /b 1
)

echo ✅ Frontend dependencies installed

REM Step 7: Start frontend
echo.
echo 🌐 Step 7: Starting frontend application...
echo -----------------------------------------------
echo Frontend will start at: http://localhost:3000
echo.
echo Starting frontend in 3 seconds...
timeout /t 3 >nul

REM Start frontend in a new window
start "AI Mental Health Frontend" cmd /c "npm start & pause"

cd ..

REM Final success message
echo.
echo ===============================================================
echo 🎉 AI Mental Health Companion Started Successfully!
echo ===============================================================
echo.
echo 🔗 Application URLs:
echo   • Frontend (Main App):     http://localhost:3000
echo   • Backend API:             http://localhost:8000
echo   • API Documentation:       http://localhost:8000/docs
echo   • AI Health Check:         http://localhost:8000/health/ai
echo.
echo 🤖 AI Features Enabled:
echo   • Google Gemini AI integration
echo   • Hybrid emotion detection (Gemini + rule-based)
echo   • Empathetic response generation
echo   • Intelligent fallback system
echo   • Real-time safety monitoring
echo.
echo 🧪 Demo Scenarios to Try:
echo   1. "I'm feeling really stressed about work"
echo   2. "I'm anxious about my presentation tomorrow"
echo   3. "I'm grateful for all the support I've received"
echo   4. "I feel overwhelmed with everything I need to do"
echo.
echo 📝 Usage Tips:
echo   • Try different emotional expressions to see Gemini respond
echo   • Notice how responses adapt to your emotional state
echo   • Explore the coping tools suggested by the AI
echo   • Check the AI health endpoint to monitor services
echo.
echo ⚠️ Important Notes:
echo   • This is a demo/development setup
echo   • Gemini API calls may incur costs
echo   • Keep your API key secure
echo   • The system will fallback to rule-based responses if Gemini fails
echo.
echo 🛑 To Stop the Services:
echo   • Close the backend server window
echo   • Close the frontend development server (Ctrl+C)
echo   • Or close this command window
echo.
echo ===============================================================
echo 🌟 Enjoy exploring the AI-powered mental health companion!
echo ===============================================================
echo.

REM Keep the window open
echo Press any key to open the application in your browser...
pause >nul

REM Open the application in default browser
start http://localhost:3000

echo.
echo Both services are now running. You can close this window anytime.
echo Check the individual service windows for logs and status.
pause
