#!/bin/bash

echo "======================================"
echo "PhishGuard.uz Training Platform"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3."
    exit 1
fi

# Check if Flask is installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Initialize database if it doesn't exist
if [ ! -f "phishguard.db" ]; then
    echo "🗄️  Initializing database..."
    python3 -c "from app import init_db; init_db()"
fi

echo "✅ Starting server..."
echo ""
echo "📱 Access the application at: http://localhost:5000"
echo ""
echo "🔐 Admin credentials:"
echo "   Username: admin"
echo "   Password: sulaymon123"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================"
echo ""

python3 app.py
