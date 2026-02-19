#!/bin/bash

# Warrior Dashboard Setup Script
# Run this to set everything up automatically

echo "⚔️  WARRIOR DASHBOARD - SETUP"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3.8 or higher from https://www.python.org/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.8"

if (( $(echo "$PYTHON_VERSION < $REQUIRED_VERSION" | bc -l) )); then
    echo "❌ Python $PYTHON_VERSION detected. Python 3.8+ required!"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"
echo ""

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing Flask..."
    pip3 install Flask
    if [ $? -eq 0 ]; then
        echo "✅ Flask installed successfully"
    else
        echo "❌ Failed to install Flask"
        exit 1
    fi
else
    echo "✅ Flask already installed"
fi

echo ""

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    echo "📁 Creating data directory..."
    mkdir data
    echo "✅ Data directory created"
else
    echo "✅ Data directory exists"
fi

echo ""
echo "================================"
echo "✅ SETUP COMPLETE!"
echo "================================"
echo ""
echo "🚀 To start the dashboard:"
echo "   python3 app.py"
echo ""
echo "📖 Then open: http://localhost:5000"
echo ""
echo "⚔️  May your stats grow strong!"
