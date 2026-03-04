"""Application Entry Point"""
import os
import sys

def main():
    """Run the application"""
    try:
        # Check if in correct directory
        if not os.path.exists('app'):
            print("❌ Error: 'app' directory not found!")
            print("\n💡 Make sure you're in the warrior-dashboard-refactored directory:")
            print("   cd warrior-dashboard-refactored")
            print("   python run.py")
            sys.exit(1)
        
        # Try to import and create app
        from app import create_app
        
        app = create_app(os.getenv('FLASK_ENV', 'development'))
        
        # Success! Start server
        print("\n" + "="*60)
        print("🚀 Warrior Dashboard Starting...")
        print("="*60)
        print(f"\n📍 Local:   http://localhost:5000")
        print(f"📍 Network: http://0.0.0.0:5000")
        print(f"\n👤 Register at: http://localhost:5000/auth/register")
        print(f"🔐 Login at:    http://localhost:5000/auth/login")
        print("\n💡 Press CTRL+C to stop the server")
        print("="*60 + "\n")
        
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except ImportError as e:
        print("\n❌ Import Error!")
        print(f"   {e}")
        print("\n💡 Possible fixes:")
        print("   1. Install dependencies:")
        print("      pip install -r requirements.txt")
        print("\n   2. Make sure you're in the right directory:")
        print("      cd warrior-dashboard-refactored")
        print("\n   3. Run debug script:")
        print("      python debug_run.py")
        sys.exit(1)
        
    except Exception as e:
        print("\n❌ Error starting application!")
        print(f"   {type(e).__name__}: {e}")
        print("\n💡 Run debug script for detailed diagnostics:")
        print("   python debug_run.py")
        import traceback
        print("\n📋 Full error traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()


