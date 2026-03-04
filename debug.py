"""Debug Script - Find Issues"""
import sys
import os

print("🔍 Warrior Dashboard Debug Script")
print("="*60)

# 1. Check Python version
print("\n1️⃣ Python Version:")
print(f"   {sys.version}")
if sys.version_info < (3, 8):
    print("   ⚠️  Python 3.8+ recommended")

# 2. Check directory
print("\n2️⃣ Current Directory:")
print(f"   {os.getcwd()}")

print("\n3️⃣ Files in Directory:")
files = os.listdir('.')
for f in ['app', 'config.py', 'run.py', 'requirements.txt']:
    status = "✅" if f in files else "❌"
    print(f"   {status} {f}")

# 4. Check if app directory has correct structure
print("\n4️⃣ App Directory Structure:")
if os.path.exists('app'):
    app_files = os.listdir('app')
    for f in ['__init__.py', 'models.py', 'features', 'routes']:
        status = "✅" if f in app_files else "❌"
        print(f"   {status} app/{f}")
else:
    print("   ❌ app/ directory missing!")

# 5. Check dependencies
print("\n5️⃣ Dependencies:")
required = ['flask', 'flask_sqlalchemy', 'flask_migrate', 'flask_login']
for pkg in required:
    try:
        __import__(pkg)
        print(f"   ✅ {pkg}")
    except ImportError:
        print(f"   ❌ {pkg} - NOT INSTALLED")

# 6. Try to import app
print("\n6️⃣ Importing App:")
try:
    from app import create_app
    print("   ✅ App import successful")
    
    # Try to create app
    print("\n7️⃣ Creating App Instance:")
    app = create_app('development')
    print("   ✅ App created successfully")
    
    # Check routes
    print("\n8️⃣ Registered Routes:")
    with app.app_context():
        for rule in app.url_map.iter_rules():
            print(f"   {rule.endpoint:30s} {rule.rule}")
    
    print("\n" + "="*60)
    print("✅ ALL CHECKS PASSED!")
    print("\nYou can now run:")
    print("   python run.py")
    print("="*60)
    
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    print("\n💡 Fix:")
    print("   pip install -r requirements.txt")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("\n📋 Full traceback:")
    import traceback
    traceback.print_exc()
    
    print("\n💡 Common fixes:")
    print("   1. Make sure you're in the right directory")
    print("   2. Install dependencies: pip install -r requirements.txt")
    print("   3. Check if .env file exists: cp .env.example .env")


