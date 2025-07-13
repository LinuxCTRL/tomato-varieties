#!/bin/bash

# Tomato Varieties Database - Startup Script

echo "🍅 Starting Tomato Varieties Database..."
echo "======================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Check if bun is available
if ! command -v bun &> /dev/null; then
    echo "❌ bun is required but not installed."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Python dependencies"
        exit 1
    fi
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
if [ -f "../frontend/package.json" ]; then
    cd ../frontend
    bun install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Node.js dependencies"
        exit 1
    fi
    cd ../backend
else
    echo "❌ package.json not found in frontend directory"
    exit 1
fi

# Check if data exists, if not run scraper
if [ ! -f "tomato_varieties.json" ]; then
    echo "📊 No data found. Running scraper to fetch initial data..."
    python3 scraper.py
    if [ $? -ne 0 ]; then
        echo "⚠️  Scraper failed, but continuing anyway..."
        echo "   You can run 'python3 scraper.py' manually later"
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
python3 api.py &
API_PID=$!

# Wait a moment for API to start
sleep 3

# Start the frontend server in background
echo "🌐 Starting Express.js frontend server (port 3000)..."
cd ../frontend
bun start &
FRONTEND_PID=$!
cd ../backend

# Wait a moment for frontend to start
sleep 3

echo ""
echo "✅ Servers started successfully!"
echo "================================"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 API:      http://localhost:5000"
echo ""
echo "📚 Available endpoints:"
echo "   GET  /                     - Home page (all varieties)"
echo "   GET  /search?q=<query>     - Search varieties"
echo "   GET  /tomato/<name>        - Individual variety details"
echo "   GET  /stats                - Database statistics"
echo ""
echo "⌨️  Keyboard shortcuts:"
echo "   Ctrl+C                     - Stop all servers"
echo "   Ctrl/Cmd+K (in browser)    - Focus search"
echo ""
echo "🔄 To refresh data:"
echo "   Run: python3 scraper.py"
echo "   Or use the refresh button in the web interface"
echo ""
echo "Press Ctrl+C to stop all servers..."

# Wait for background processes
wait $API_PID $FRONTEND_PID
