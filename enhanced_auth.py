#!/usr/bin/env python3
"""
Monster Hunter Frontier G - Enhanced Authentication System
Mimics the real MHF authentication process
"""

import hashlib
import time
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

class MHFEnhancedAuth:
    def __init__(self):
        self.db_path = Path("server_data/auth.db")
        self.init_database()
        
    def init_database(self):
        """Initialize the authentication database"""
        self.db_path.parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_date TEXT NOT NULL,
                last_login TEXT,
                is_active BOOLEAN DEFAULT 1,
                subscription_status TEXT DEFAULT 'free',
                subscription_expiry TEXT
            )
        ''')
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                created_date TEXT NOT NULL,
                expires_date TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create character data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                character_name TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                hr INTEGER DEFAULT 1,
                exp INTEGER DEFAULT 0,
                guild_rank INTEGER DEFAULT 0,
                created_date TEXT NOT NULL,
                last_login TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Insert sample data
        self.create_sample_data(cursor)
        
        conn.commit()
        conn.close()
        
    def create_sample_data(self, cursor):
        """Create sample users and characters"""
        # Sample users
        sample_users = [
            ('hunter001', 'password123', 'hunter001@example.com'),
            ('dragon_slayer', 'password123', 'dragon@example.com'),
            ('frontier_elite', 'password123', 'elite@example.com'),
            ('test_user', 'password123', 'test@example.com')
        ]
        
        for username, password, email in sample_users:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, password_hash, email, created_date)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, email, datetime.now().isoformat()))
        
        # Sample characters
        sample_characters = [
            (1, 'Hunter001', 15, 5, 15000, 2),
            (2, 'DragonSlayer', 25, 8, 45000, 3),
            (3, 'FrontierElite', 35, 12, 85000, 4),
            (4, 'TestHunter', 1, 1, 0, 0)
        ]
        
        for user_id, char_name, level, hr, exp, guild_rank in sample_characters:
            cursor.execute('''
                INSERT OR IGNORE INTO characters (user_id, character_name, level, hr, exp, guild_rank, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, char_name, level, hr, exp, guild_rank, datetime.now().isoformat()))
    
    def hash_password(self, password):
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, username, password):
        """Verify a user's password"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT password_hash FROM users WHERE username = ? AND is_active = 1', (username,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            stored_hash = result[0]
            return stored_hash == self.hash_password(password)
        return False
    
    def create_session(self, user_id, ip_address, user_agent):
        """Create a new session for a user"""
        session_token = hashlib.sha256(f"{user_id}{time.time()}".encode()).hexdigest()
        expires_date = (datetime.now() + timedelta(hours=24)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (user_id, session_token, created_date, expires_date, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, session_token, datetime.now().isoformat(), expires_date, ip_address, user_agent))
        
        # Update last login
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                      (datetime.now().isoformat(), user_id))
        
        conn.commit()
        conn.close()
        
        return session_token
    
    def validate_session(self, session_token):
        """Validate a session token"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.user_id, u.username, s.expires_date 
            FROM sessions s 
            JOIN users u ON s.user_id = u.id 
            WHERE s.session_token = ? AND s.expires_date > ?
        ''', (session_token, datetime.now().isoformat()))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'user_id': result[0],
                'username': result[1],
                'expires_date': result[2]
            }
        return None
    
    def get_user_characters(self, user_id):
        """Get all characters for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, character_name, level, hr, exp, guild_rank, created_date, last_login
            FROM characters 
            WHERE user_id = ?
        ''', (user_id,))
        
        characters = []
        for row in cursor.fetchall():
            characters.append({
                'id': row[0],
                'name': row[1],
                'level': row[2],
                'hr': row[3],
                'exp': row[4],
                'guild_rank': row[5],
                'created_date': row[6],
                'last_login': row[7]
            })
        
        conn.close()
        return characters
    
    def authenticate_user(self, username, password, ip_address, user_agent):
        """Authenticate a user and create session"""
        if not self.verify_password(username, password):
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            user_id, username = result
            session_token = self.create_session(user_id, ip_address, user_agent)
            
            return {
                'user_id': user_id,
                'username': username,
                'session_token': session_token,
                'server_time': int(time.time()),
                'status': 'success'
            }
        
        return None
    
    def get_user_info(self, session_token):
        """Get user information from session token"""
        session = self.validate_session(session_token)
        if not session:
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, created_date, last_login, subscription_status, subscription_expiry
            FROM users WHERE id = ?
        ''', (session['user_id'],))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'user_id': result[0],
                'username': result[1],
                'email': result[2],
                'created_date': result[3],
                'last_login': result[4],
                'subscription_status': result[5],
                'subscription_expiry': result[6],
                'characters': self.get_user_characters(session['user_id'])
            }
        
        return None

def main():
    """Test the enhanced authentication system"""
    auth = MHFEnhancedAuth()
    
    print("🐉 Monster Hunter Frontier G - Enhanced Authentication Test")
    print("=" * 60)
    
    # Test authentication
    print("\n--- Testing Authentication ---")
    result = auth.authenticate_user('hunter001', 'password123', '127.0.0.1', 'TestClient/1.0')
    
    if result:
        print(f"✓ Authentication successful!")
        print(f"  User: {result['username']}")
        print(f"  Session Token: {result['session_token'][:16]}...")
        print(f"  Server Time: {result['server_time']}")
        
        # Test session validation
        print("\n--- Testing Session Validation ---")
        user_info = auth.get_user_info(result['session_token'])
        
        if user_info:
            print(f"✓ Session validated!")
            print(f"  User ID: {user_info['user_id']}")
            print(f"  Characters: {len(user_info['characters'])}")
            for char in user_info['characters']:
                print(f"    - {char['name']} (HR{char['hr']}, Level {char['level']})")
    else:
        print("✗ Authentication failed!")

if __name__ == "__main__":
    main() 