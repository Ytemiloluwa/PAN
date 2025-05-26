
import hashlib
import os
import logging
from ..infrastructure.database import get_db_connection, initialize_schema

# Constants for password hashing
HASH_ALGORITHM = 'sha256'
SALT_BYTES = 16
PBKDF2_ITERATIONS_AUTH = 200000 # Use a higher iteration count for password hashing than DB key

def hash_password(password: str, salt: bytes = None) -> tuple[str, bytes]:
    """Hashes a password using PBKDF2-HMAC-SHA256."""
    if salt is None:
        salt = os.urandom(SALT_BYTES)
    
    key = hashlib.pbkdf2_hmac(
        hash_name=HASH_ALGORITHM,
        password=password.encode("utf-8"),
        salt=salt,
        iterations=PBKDF2_ITERATIONS_AUTH
    )
    # Store the hash as hex, salt as is (or hex)
    return key.hex(), salt

def verify_password(stored_hash_hex: str, provided_password: str, salt: bytes) -> bool:
    """Verifies a provided password against a stored hash and salt."""
    try:
        stored_key = bytes.fromhex(stored_hash_hex)
    except ValueError:
        logging.error("Invalid stored hash format.")
        return False
        
    new_key = hashlib.pbkdf2_hmac(
        hash_name=HASH_ALGORITHM,
        password=provided_password.encode("utf-8"),
        salt=salt,
        iterations=PBKDF2_ITERATIONS_AUTH
    )
    # Use compare_digest for timing attack resistance
    return hashlib.compare_digest(stored_key, new_key)

def create_user(db_password: str, username: str, password: str) -> bool:
    """Creates a new user in the database."""
    conn = None
    try:
        conn = get_db_connection(db_password)
        initialize_schema(conn) # Ensure schema exists
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            logging.warning(f"Username 	{username}	 already exists.")
            return False

        # Hash the user's login password
        password_hash_hex, salt = hash_password(password)

        cursor.execute("""
        INSERT INTO users (username, password_hash, salt) 
        VALUES (?, ?, ?)
        """, (username, password_hash_hex, salt))
        
        conn.commit()
        logging.info(f"User 	{username}	 created successfully.")
        return True

    except Exception as e:
        logging.error(f"Error creating user 	{username}	: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def authenticate_user(db_password: str, username: str, password: str) -> bool:
    """Authenticates a user against the database."""
    conn = None
    try:
        conn = get_db_connection(db_password)
        initialize_schema(conn) # Ensure schema exists
        cursor = conn.cursor()

        cursor.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()

        if not result:
            logging.warning(f"Login attempt failed: User 	{username}	 not found.")
            return False

        stored_hash_hex, salt = result
        
        if verify_password(stored_hash_hex, password, salt):
            logging.info(f"User 	{username}	 authenticated successfully.")
            return True
        else:
            logging.warning(f"Login attempt failed: Invalid password for user 	{username}	.")
            return False

    except Exception as e:
        logging.error(f"Error authenticating user 	{username}	: {e}")
        return False
    finally:
        if conn:
            conn.close()

# Example usage (for testing, remove later)
# if __name__ == '__main__':
#     db_pass = "testpassword123"
#     # Ensure the .fintechx directory exists
#     db_dir = os.path.join(os.path.expanduser("~"), ".fintechx")
#     if not os.path.exists(db_dir):
#         os.makedirs(db_dir)
#     
#     # Clean up old db/salt for testing
#     db_file = os.path.join(db_dir, "fintechx_data.db")
#     salt_file = db_file + ".salt"
#     if os.path.exists(db_file): os.remove(db_file)
#     if os.path.exists(salt_file): os.remove(salt_file)
# 
#     print("Creating user 'testuser'...")
#     create_user(db_pass, "testuser", "password123")
#     print("Authenticating 'testuser' with correct password...")
#     print(f"Authentication result: {authenticate_user(db_pass, 'testuser', 'password123')}")
#     print("Authenticating 'testuser' with incorrect password...")
#     print(f"Authentication result: {authenticate_user(db_pass, 'testuser', 'wrongpassword')}")
#     print("Authenticating non-existent user 'nouser'...")
#     print(f"Authentication result: {authenticate_user(db_pass, 'nouser', 'password123')}")


