#!/bin/bash
set -e

echo "🚀 Starting Evalence Security Testing Platform..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Start the backend server
echo "✅ Starting FastAPI server..."
python backend/run.py