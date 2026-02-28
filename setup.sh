#!/bin/bash

echo "🚀 Warrior Dashboard Setup"
echo "=========================="
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found!"
    echo "Please run this script from the warrior-dashboard-refactored directory:"
    echo "  cd warrior-dashboard-refactored"
    echo "  bash setup.sh"
    exit 1
fi

echo "📦 Step 1: Installing dependencies..."
pip install -r requirements.txt --break-system-packages || pip install -r requirements.txt

echo ""
echo "⚙️  Step 2: Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  IMPORTANT: Edit .env and set SECRET_KEY=your-random-key-here"
else
    echo "✅ .env already exists"
fi

echo ""
echo "🗄️  Step 3: Setting up database..."
export FLASK_APP=run.py

# Initialize database if not already done
if [ ! -d "migrations" ]; then
    flask db init
    echo "✅ Database initialized"
else
    echo "✅ Database already initialized"
fi

# Create migration
flask db migrate -m "Initial schema" 2>/dev/null || echo "Migration already exists"

# Apply migration
flask db upgrade

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo "  python run.py"
echo ""
echo "Then visit: http://localhost:5000/auth/register"
echo ""
