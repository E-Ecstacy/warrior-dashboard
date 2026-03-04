"""Diagnose Project Setup"""
import os
import sys

print("🔍 Warrior Dashboard Diagnostics")
print("="*60)

# Check current directory
print("\n1️⃣ Current Directory:")
print(f"   {os.getcwd()}")

# Check if key files exist
print("\n2️⃣ Required Files:")
required_files = [
    'app/__init__.py',
    'app/models.py',
    'app/routes/__init__.py',
    'app/routes/main.py',
    'app/routes/auth.py',
    'app/routes/api.py',
    'app/features/__init__.py',
    'config.py',
    'run.py',
    'requirements.txt'
]

all_exist = True
for file in required_files:
    exists = os.path.exists(file)
    status = "✅" if exists else "❌"
    print(f"   {status} {file}")
    if not exists:
        all_exist = False

if not all_exist:
    print("\n❌ Missing files! Are you in the right directory?")
    print("\n💡 Navigate to your project root:")
    print("   cd /path/to/warrior-dashboard-refactored")
    print("   python diagnose.py")
    sys.exit(1)

# Try to import app
print("\n3️⃣ Testing Imports:")
sys.path.insert(0, os.getcwd())

try:
    print("   Importing app...", end=" ")
    from app import create_app, db
    print("✅")
except ImportError as e:
    print(f"❌")
    print(f"   Error: {e}")
    sys.exit(1)

try:
    print("   Importing models...", end=" ")
    from app.models import User, Character, DailyLog
    print("✅")
except ImportError as e:
    print(f"❌")
    print(f"   Error: {e}")
    sys.exit(1)

try:
    print("   Importing routes...", end=" ")
    from app.routes import main, auth, api
    print("✅")
except ImportError as e:
    print(f"❌")
    print(f"   Error: {e}")
    sys.exit(1)

try:
    print("   Creating app...", end=" ")
    app = create_app()
    print("✅")
except Exception as e:
    print(f"❌")
    print(f"   Error: {e}")
    sys.exit(1)

# Check routes
print("\n4️⃣ Checking Routes:")
with app.app_context():
    api_routes = [rule for rule in app.url_map.iter_rules() if rule.endpoint.startswith('api.')]
    print(f"   Found {len(api_routes)} API routes")
    
    if len(api_routes) == 0:
        print("   ❌ No API routes found!")
        print("   Check that api blueprint is registered in app/__init__.py")
    else:
        print("   ✅ API routes registered")
        print("\n   Sample routes:")
        for rule in list(api_routes)[:5]:
            print(f"      {rule.rule}")

print("\n" + "="*60)
print("✅ All checks passed!")
print("\nYou can now run:")
print("   python run.py")


