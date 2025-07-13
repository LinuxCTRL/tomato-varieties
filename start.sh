#!/bin/bash

# Tomato Varieties Database - Main Startup Script
# Organized Structure: backend/ + frontend/

echo "🍅 Starting Tomato Varieties Database..."
echo "======================================"

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: backend/ and frontend/ directories not found"
    echo "   Make sure you're running this from the project root"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "[+] Please install Python 3.7 or higher from https://www.python.org/"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "[+] Please install Node.js (version 14 or higher) from https://nodejs.org/"
    exit 1
fi

# Check if bun is available (fallback to npm)
if command -v bun &> /dev/null; then
    NODE_MANAGER="bun"
    INSTALL_CMD="bun install"
    START_CMD="bun start"
elif command -v npm &> /dev/null; then
    NODE_MANAGER="npm"
    INSTALL_CMD="npm install"
    START_CMD="npm start"
else
    echo "❌ Neither bun nor npm is available."
    exit 1
fi

echo "✅ Prerequisites check passed (using $NODE_MANAGER)"

# Set up Python virtual environment and install dependencies
echo "📦 Setting up Python virtual environment..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating Python virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Python dependencies"
        exit 1
    fi
else
    echo "❌ requirements.txt not found in backend/"
    exit 1
fi

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd ../frontend
if [ -f "package.json" ]; then
    $INSTALL_CMD
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Node.js dependencies"
        exit 1
    fi
else
    echo "❌ package.json not found in frontend/"
    exit 1
fi

# Go back to backend for data check
cd ../backend

# Check if data exists, if not run scraper
if [ ! -f "tomato_varieties.json" ]; then
    echo "📊 No data found. Running scraper to fetch initial data..."
    python3 scraper.py
    if [ $? -ne 0 ]; then
        echo "⚠️  Scraper failed, but continuing anyway..."
        echo "   You can run 'cd backend && python3 scraper.py' manually later"
    fi
else
    echo "✅ Data file found"
fi

echo ""
echo "🚀 Starting servers..."
echo "====================="

# Function to kill background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $API_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start the API server in background
echo "🔧 Starting Python API server (port 5000)..."
cd backend
source venv/bin/activate
python api.py &
API_PID=$!

# Wait a moment for API to start
sleep 3

# Start the frontend server in background
echo "🌐 Starting Express.js frontend server (port 3000)..."
cd ../frontend
$START_CMD &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 3

echo ""
echo "✅ Servers started successfully!"
echo "================================"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 API:      http://localhost:5000"
echo ""
echo "📚 Available pages:"
echo "   GET  /                     - Home page (all varieties)"
echo "   GET  /search?q=<query>     - Search varieties"
echo "   GET  /tomato/<name>        - Individual variety details"
echo "   GET  /stats                - Database statistics"
echo "   GET  /loading-demo         - Loading animations demo"
echo ""
echo "🎨 Features:"
echo "   🌙 Dark mode toggle        - Top right corner"
echo "   🎪 Loading animations      - Beautiful progress indicators"
echo "   🍅 Rich variety data       - Comprehensive tomato info"
echo "   📱 Responsive design       - Works on all devices"
echo ""
echo "⌨️  Keyboard shortcuts:"
echo "   Ctrl+C                     - Stop all servers"
echo "   Ctrl/Cmd+K (in browser)    - Focus search"
echo ""
echo "🔄 To refresh data:"
echo "   Run: cd backend && python3 scraper.py"
echo "   Or use the refresh button in the web interface"
echo ""
echo "Press Ctrl+C to stop all servers..."

# Wait for background processes
wait $API_PID $FRONTEND_PID
