import sqlite3
import json
from pathlib import Path
from datetime import datetime
from config import Config

def get_db_connection():
    """Get SQLite database connection"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Face embeddings table - stores DeepFace VGGFace embeddings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS face_embeddings (
            user_id TEXT PRIMARY KEY,
            embedding TEXT NOT NULL,
            model_name TEXT DEFAULT 'VGG-Face',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # License records table - stores OCR extracted data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS license_records (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            license_number TEXT UNIQUE,
            dob TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES face_embeddings(user_id) ON DELETE CASCADE
        )
    ''')
    
    # Verification logs table - audit trail
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verification_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            verification_status TEXT,
            face_confidence REAL,
            license_match_score REAL,
            liveness_passed BOOLEAN,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES face_embeddings(user_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")
    print(f"📁 Database location: {Path(Config.DATABASE_PATH).absolute()}")

# ========== FACE EMBEDDINGS OPERATIONS ==========

def store_face_embedding(user_id, embedding_list, model_name='VGG-Face'):
    """Store face embedding in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    embedding_json = json.dumps(embedding_list)
    
    cursor.execute('''
        INSERT OR REPLACE INTO face_embeddings (user_id, embedding, model_name, updated_at)
        VALUES (?, ?, ?, ?)
    ''', (user_id, embedding_json, model_name, datetime.now()))
    
    conn.commit()
    conn.close()
    print(f"✅ Face embedding stored for user: {user_id}")

def get_face_embedding(user_id):
    """Get face embedding for specific user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT embedding FROM face_embeddings WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return json.loads(row['embedding'])
    return None

def get_all_face_embeddings():
    """Get all face embeddings for verification"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT user_id, embedding FROM face_embeddings')
    rows = cursor.fetchall()
    conn.close()
    
    return [(row['user_id'], json.loads(row['embedding'])) for row in rows]

# ========== LICENSE RECORDS OPERATIONS ==========

def store_license_record(user_id, license_data):
    """Store license record in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO license_records 
        (user_id, name, license_number, dob, address, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        license_data.get('name'),
        license_data.get('license_number'),
        license_data.get('dob'),
        license_data.get('address', ''),
        datetime.now()
    ))
    
    conn.commit()
    conn.close()
    print(f"✅ License record stored for user: {user_id}")

def get_license_record(user_id):
    """Get license record for specific user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT name, license_number, dob, address 
        FROM license_records 
        WHERE user_id = ?
    ''', (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'name': row['name'],
            'license_number': row['license_number'],
            'dob': row['dob'],
            'address': row['address']
        }
    return None

# ========== VERIFICATION LOGS ==========

def log_verification(user_id, status, face_confidence, license_match_score, liveness_passed):
    """Log verification attempt"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO verification_logs 
        (user_id, verification_status, face_confidence, license_match_score, liveness_passed)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, status, face_confidence, license_match_score, liveness_passed))
    
    conn.commit()
    conn.close()

def get_verification_logs(limit=50):
    """Get recent verification logs"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM verification_logs 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

# ========== USER MANAGEMENT ==========

def get_all_users():
    """Get list of all registered users"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            f.user_id, 
            f.created_at, 
            f.model_name,
            l.name, 
            l.license_number,
            l.dob
        FROM face_embeddings f
        LEFT JOIN license_records l ON f.user_id = l.user_id
        ORDER BY f.created_at DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def delete_user_data(user_id):
    """Delete all data for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM license_records WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM face_embeddings WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM verification_logs WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()
    print(f"✅ User {user_id} deleted successfully")

def user_exists(user_id):
    """Check if user exists"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT 1 FROM face_embeddings WHERE user_id = ?', (user_id,))
    exists = cursor.fetchone() is not None
    
    conn.close()
    return exists
