@echo off
REM Tomato Varieties Database - Windows Startup Script
REM Organized Structure: backend/ + frontend/

echo 🍅 Starting Tomato Varieties Database...
echo ======================================

REM Check if we're in the right directory
if not exist "backend" (
    echo ❌ Error: backend/ directory not found
    echo    Make sure you're running this from the project root
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ❌ Error: frontend/ directory not found
    echo    Make sure you're running this from the project root
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed.
    echo    Please install Python 3.7 or higher from https://www.python.org/
    echo    Make sure to add it to your PATH during installation
    pause
    exit /b 1

)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is required but not installed.
    echo    Please install Node.js (version 14 or higher) from https://nodejs.org/
    echo    Make sure to add it to your PATH during installation
    echo    If you have installed Node.js, try restarting your terminal or computer
    echo    to ensure the PATH is updated.
    echo    If you still see this error, check your Node.js installation
    echo    and ensure it is correctly set up.
    echo    You can verify your Node.js installation by running 'node --version' in a command prompt.
    echo    If you see a version number, Node.js is installed correctly.
    echo    If you see an error, please reinstall Node.js.
    pause
    exit /b 1
)

REM Check if npm is available
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is required but not installed.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Set up Python virtual environment and install dependencies
echo 📦 Setting up Python virtual environment...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 🔧 Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call .venv\Scripts\activate

REM Install Python dependencies
echo 📦 Installing Python dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install Python dependencies
        pause
        exit /b 1
    )
) else (
    echo ❌ requirements.txt not found in backend/
    pause
    exit /b 1
)

REM Install Node.js dependencies
echo 📦 Installing Node.js dependencies...
cd ..\frontend
if exist "package.json" (
    npm install
    if errorlevel 1 (
        echo ❌ Failed to install Node.js dependencies
        pause
        exit /b 1
    )
) else (
    echo ❌ package.json not found in frontend/
    pause
    exit /b 1
)

REM Go back to backend for data check
cd ..\backend

REM Check if data exists, if not run scraper
if not exist "tomato_varieties.json" (
    echo 📊 No data found. Running scraper to fetch initial data...
    call venv\Scripts\activate
    python scraper.py
    if errorlevel 1 (
        echo ⚠️  Scraper failed, but continuing anyway...
        echo    You can run 'cd backend && venv\Scripts\activate && python scraper.py' manually later
    )
) else (
    echo ✅ Data file found
)

echo.
echo 🚀 Starting servers...
echo =====================

REM Start the API server in background
echo 🔧 Starting Python API server (port 5000)...
call venv\Scripts\activate
start "API Server" cmd /k "python api.py"

REM Wait a moment for API to start
timeout /t 3 /nobreak >nul

REM Start the frontend server in background
echo 🌐 Starting Express.js frontend server (port 3000)...
cd ..\frontend
start "Frontend Server" cmd /k "npm start"

REM Wait a moment for frontend to start
timeout /t 3 /nobreak >nul

echo.
echo ✅ Servers started successfully!
echo ================================
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔧 API:      http://localhost:5000
echo.
echo 📚 Available pages:
echo    GET  /                     - Home page (all varieties)
echo    GET  /search?q=^<query^>     - Search varieties
echo    GET  /tomato/^<name^>        - Individual variety details
echo    GET  /stats                - Database statistics
echo    GET  /loading-demo         - Loading animations demo
echo.
echo 🎨 Features:
echo    🌙 Dark mode toggle        - Top right corner
echo    🎪 Loading animations      - Beautiful progress indicators
echo    🍅 Rich variety data       - Comprehensive tomato info
echo    📱 Responsive design       - Works on all devices
echo.
echo 🔄 To refresh data:
echo    Run: cd backend ^&^& venv\Scripts\activate ^&^& python scraper.py
echo    Or use the refresh button in the web interface
echo.
echo Press any key to open the application in your browser...
pause >nul

REM Open browser
start http://localhost:3000

echo.
echo 🎉 Application opened in browser!
echo Close the command windows to stop the servers.
pause
