"""
Database Adapter - Supports both JSON and SQLite storage
Automatically uses SQLite if available, falls back to JSON
"""

import json
import os
from datetime import datetime

# Try to import sqlite3
try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

class DatabaseAdapter:
    """Hybrid database adapter supporting JSON and SQLite"""
    
    def __init__(self, storage_type='sqlite'):
        """
        Initialize database adapter
        
        Args:
            storage_type: 'json', 'sqlite', or 'auto' (default: 'sqlite')
                         'auto' uses SQLite if available
        """
        self.json_file = 'data/character_data.json'
        self.sqlite_file = 'data/warrior_dashboard.db'
        
        # Determine storage type
        if storage_type == 'auto':
            # Prefer SQLite if available
            if SQLITE_AVAILABLE:
                self.storage_type = 'sqlite'
            else:
                self.storage_type = 'json'
        elif storage_type == 'sqlite' and not SQLITE_AVAILABLE:
            print("⚠️  SQLite not available, falling back to JSON")
            self.storage_type = 'json'
        else:
            self.storage_type = storage_type
        
        # Initialize storage
        if self.storage_type == 'sqlite' and SQLITE_AVAILABLE:
            self._init_sqlite()
        else:
            self.storage_type = 'json'  # Fallback to JSON
    
    def _init_sqlite(self):
        """Initialize SQLite database with schema"""
        conn = sqlite3.connect(self.sqlite_file)
        cursor = conn.cursor()
        
        # Main data table (stores JSON blob for simplicity)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS character_data (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                data TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Optional: Separate tables for better querying (future optimization)
        # For now, we'll just use JSON blob for compatibility
        
        conn.commit()
        conn.close()
    
    def load_data(self):
        """Load data from current storage"""
        if self.storage_type == 'sqlite':
            return self._load_sqlite()
        else:
            return self._load_json()
    
    def save_data(self, data):
        """Save data to current storage"""
        if self.storage_type == 'sqlite':
            self._save_sqlite(data)
        else:
            self._save_json(data)
    
    def _load_json(self):
        """Load from JSON file"""
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r') as f:
                return json.load(f)
        return None
    
    def _save_json(self, data):
        """Save to JSON file"""
        os.makedirs('data', exist_ok=True)
        with open(self.json_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_sqlite(self):
        """Load from SQLite database"""
        conn = sqlite3.connect(self.sqlite_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT data FROM character_data WHERE id = 1')
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return None
    
    def _save_sqlite(self, data):
        """Save to SQLite database"""
        os.makedirs('data', exist_ok=True)
        conn = sqlite3.connect(self.sqlite_file)
        cursor = conn.cursor()
        
        json_data = json.dumps(data, indent=2)
        
        # Insert or replace
        cursor.execute('''
            INSERT OR REPLACE INTO character_data (id, data, updated_at)
            VALUES (1, ?, CURRENT_TIMESTAMP)
        ''', (json_data,))
        
        conn.commit()
        conn.close()
    
    def get_storage_type(self):
        """Get current storage type"""
        return self.storage_type
    
    def migrate_to_sqlite(self):
        """Migrate from JSON to SQLite"""
        if not SQLITE_AVAILABLE:
            raise Exception("SQLite not available")
        
        # Load existing JSON data
        json_data = self._load_json()
        if not json_data:
            raise Exception("No JSON data to migrate")
        
        # Initialize SQLite
        self._init_sqlite()
        
        # Save to SQLite
        self._save_sqlite(json_data)
        
        # Backup JSON file
        backup_file = f"{self.json_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if os.path.exists(self.json_file):
            os.rename(self.json_file, backup_file)
        
        # Switch to SQLite
        self.storage_type = 'sqlite'
        
        return backup_file
    
    def export_to_json(self, filepath=None):
        """Export current data to JSON file"""
        if filepath is None:
            filepath = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = self.load_data()
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filepath


# Global instance
db = DatabaseAdapter(storage_type='auto')


def get_db():
    """Get database adapter instance"""
    return db
