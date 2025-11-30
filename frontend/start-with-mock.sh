#!/bin/bash

echo "🚀 Starting OneStep Frontend with Mock API"
echo "=========================================="
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
    echo ""
fi

# Check if json-server is installed
if ! npm list json-server > /dev/null 2>&1; then
    echo "📦 Installing json-server..."
    npm install --save-dev json-server concurrently
    echo "✅ json-server installed"
    echo ""
fi

echo "🎯 Starting services..."
echo ""
echo "Mock API will be available at: http://localhost:8000"
echo "Frontend will be available at: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start both services
npm run dev:mock
