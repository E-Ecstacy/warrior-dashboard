#!/usr/bin/env python3
"""
Warrior Dashboard - JSON to SQLite Migration
Migrates your data from JSON to SQLite database
"""

import os
import sys
import json
from datetime import datetime

def main():
    print("=" * 60)
    print("WARRIOR DASHBOARD - JSON TO SQLITE MIGRATION")
    print("=" * 60)
    print()
    
    json_file = 'data/character_data.json'
    sqlite_file = 'data/warrior_dashboard.db'
    
    # Check if JSON file exists
    if not os.path.exists(json_file):
        print("❌ No JSON file found")
        print("   If you're a new user, just run: python app.py")
        return 1
    
    # Check if SQLite already exists
    if os.path.exists(sqlite_file):
        print(f"⚠️  SQLite database already exists")
        response = input("Overwrite? (yes/no): ").lower()
        if response != 'yes':
            print("Cancelled.")
            return 0
    
    # Load JSON
    print("📖 Reading JSON data...")
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        print(f"✅ Loaded data")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    # Create SQLite
    print("🗄️  Creating SQLite database...")
    try:
        import sqlite3
        os.makedirs('data', exist_ok=True)
        
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS character_data (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                data TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            INSERT OR REPLACE INTO character_data (id, data, updated_at)
            VALUES (1, ?, CURRENT_TIMESTAMP)
        ''', (json.dumps(data, indent=2),))
        
        conn.commit()
        conn.close()
        print("✅ SQLite created")
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    # Backup JSON
    print("💾 Backing up JSON...")
    backup = f"{json_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        os.rename(json_file, backup)
        print(f"✅ Backup: {backup}")
    except Exception as e:
        print(f"⚠️  Backup failed: {e}")
    
    print()
    print("✅ MIGRATION COMPLETE!")
    print(f"  Database: {sqlite_file}")
    print(f"  Backup: {backup}")
    print()
    print("Run: python app.py")
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n❌ Cancelled")
        sys.exit(1)
