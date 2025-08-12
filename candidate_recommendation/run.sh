#!/bin/bash

# Candidate Recommendation System Startup Script

echo "🚀 Starting Candidate Recommendation System..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if requirements are installed
if ! python3 -c "import fastapi, uvicorn, sentence_transformers" &> /dev/null; then
    echo "📦 Installing requirements..."
    pip3 install -r requirements.txt
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file from template..."
    cp env.example .env
    echo "✅ Created .env file. Please edit it with your preferred settings."
fi

# Start the system
echo "🔧 Starting FastAPI server on port 8001..."
echo "📖 API documentation will be available at: http://localhost:8001/docs"
echo "🔍 Health check: http://localhost:8001/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 main.py --api
