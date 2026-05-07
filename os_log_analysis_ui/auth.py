import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="NewPassword123",
    database="oslog_analysis"
)

cursor = conn.cursor()

# Ensure password column exists
try:
    cursor.execute('ALTER TABLE users ADD COLUMN password VARCHAR(255) AFTER username')
    conn.commit()
    print("✓ Password column added to users table")
except mysql.connector.Error as e:
    if 'Duplicate column' not in str(e):
        print(f"Database migration note: {e}")
    # Column already exists, no action needed
    pass

def register_user(username, password, email, role='Viewer'):
    """Register a new user"""
    try:
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        cursor.execute(
            "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)",
            (username, hashed_password, email, role)
        )
        conn.commit()
        return True, "User registered successfully!"
    except mysql.connector.errors.IntegrityError as e:
        if 'username' in str(e):
            return False, "Username already exists!"
        elif 'email' in str(e):
            return False, "Email already exists!"
        return False, str(e)
    except Exception as e:
        return False, str(e)

def authenticate_user(username, password):
    """Authenticate user and return user data"""
    try:
        cursor.execute(
            "SELECT user_id, username, email, role FROM users WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()
        
        if not user:
            return False, None, "Username not found!"
        
        # Get stored password
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        stored_password = result[0] if result else None
        
        if not stored_password or not check_password_hash(stored_password, password):
            return False, None, "Invalid password!"
        
        # Update last_login
        cursor.execute(
            "UPDATE users SET last_login = %s WHERE username = %s",
            (datetime.now(), username)
        )
        conn.commit()
        
        user_data = {
            'user_id': user[0],
            'username': user[1],
            'email': user[2],
            'role': user[3]
        }
        
        return True, user_data, "Login successful!"
    except Exception as e:
        return False, None, str(e)

def get_user(user_id):
    """Get user by ID"""
    try:
        cursor.execute(
            "SELECT user_id, username, email, role FROM users WHERE user_id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        
        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'email': user[2],
                'role': user[3]
            }
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def get_user_by_username(username):
    """Get user by username"""
    try:
        cursor.execute(
            "SELECT user_id, username, email, role FROM users WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()
        
        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'email': user[2],
                'role': user[3]
            }
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None
