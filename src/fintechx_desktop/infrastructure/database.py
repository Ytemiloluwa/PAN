
import os
import logging
from pysqlcipher3 import dbapi2 as sqlite

# Import the native C++ module for key derivation
# Note: This assumes the C++ module is built and available in the python path
# The build process needs to handle placing the .so/.pyd file correctly.
# For now, we might need a placeholder or assume it's built.
try:
    # This is the name defined in CMakeLists.txt (pybind11_add_module)
    from fintechx_desktop.infrastructure import fintechx_native
except ImportError:
    logging.error("Native C++ module (fintechx_native) not found. Ensure it's built and installed.")
    # Provide dummy functions or raise an error if native module is critical
    class DummyNative:
        def derive_key_pbkdf2(self, password, salt, iterations, key_length):
            # WARNING: Insecure placeholder for development without C++ build
            # Replace with actual error handling or ensure build works
            logging.warning("Using insecure dummy key derivation!")
            return b'0' * key_length # Return dummy bytes
        def generate_random_bytes(self, length):
            logging.warning("Using insecure dummy random bytes!")
            return os.urandom(length) # Use os.urandom as fallback

    fintechx_native = DummyNative()

DATABASE_FILE = "fintechx_data.db"
DATABASE_PATH = os.path.join(os.path.expanduser("~"), ".fintechx", DATABASE_FILE) # Store in user's home dir
PBKDF2_ITERATIONS = 150000 # Number of iterations for key derivation
SALT_LENGTH = 16 # Bytes
DB_KEY_LENGTH = 32 # Bytes (for AES-256)

# Ensure the storage directory exists
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

# --- Database Initialization and Schema --- 

def get_db_connection(db_password: str) -> sqlite.Connection:
    """Establishes a connection to the encrypted SQLite database."""
    conn = None
    try:
        conn = sqlite.connect(DATABASE_PATH)

        # Derive the database key from the password
        # We need a persistent salt for the database key derivation.
        # This salt should be stored securely, but NOT in the database itself.
        # For a desktop app, storing it in a separate config file or using OS keychain might be options.
        # For simplicity here, we'll store it alongside the DB, but this is NOT ideal for production.
        salt_path = DATABASE_PATH + ".salt"
        if os.path.exists(salt_path):
            with open(salt_path, "rb") as f:
                salt = f.read()
        else:
            salt = fintechx_native.generate_random_bytes(SALT_LENGTH)
            with open(salt_path, "wb") as f:
                f.write(salt)

        db_key_bytes = fintechx_native.derive_key_pbkdf2(
            db_password,
            salt,
            PBKDF2_ITERATIONS,
            DB_KEY_LENGTH
        )
        # SQLCipher expects the key as a hex string
        db_key_hex = db_key_bytes.hex()

        # Set the key PRAGMA - THIS MUST BE THE FIRST OPERATION
        conn.execute(f"PRAGMA key = 'x\"{db_key_hex}\"' ")

        # Set secure PRAGMA settings (do this after setting the key)
        conn.execute("PRAGMA cipher_page_size = 4096;")
        conn.execute(f"PRAGMA kdf_iter = {PBKDF2_ITERATIONS};") # Match iterations used for key derivation
        conn.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA256;")
        conn.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA256;")

        # Test the key by trying to access data (e.g., schema version)
        # This will fail if the key is incorrect
        conn.execute("SELECT count(*) FROM sqlite_master;")

        logging.info(f"Successfully connected to encrypted database: {DATABASE_PATH}")
        return conn

    except sqlite.Error as e:
        logging.error(f"Database connection or key error: {e}")
        if conn:
            conn.close()
        # Re-raise or handle appropriately (e.g., prompt user for correct password)
        raise ConnectionError(f"Failed to connect/unlock database: {e}") from e
    except Exception as e:
        logging.error(f"Unexpected error during DB connection: {e}")
        if conn:
            conn.close()
        raise

def initialize_schema(conn: sqlite.Connection):
    """Initializes the database schema if it doesn't exist."""
    try:
        cursor = conn.cursor()

        # Create users table (example)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, -- Store hash of the login password, not the DB key
            salt TEXT NOT NULL, -- Salt for the login password hash
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Create accounts table (example)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL, -- e.g., 'checking', 'savings', 'credit_card'
            balance REAL DEFAULT 0.0,
            currency TEXT DEFAULT 'USD',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """)

        # Create transactions table (example)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            category TEXT,
            transaction_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        );
        """)

        # Add other tables as needed (budgets, goals, invoices, etc.)

        conn.commit()
        logging.info("Database schema initialized or verified.")

    except sqlite.Error as e:
        logging.error(f"Schema initialization error: {e}")
        conn.rollback() # Rollback changes if schema creation fails
        raise

# Example usage (will be called from application layer)
# def setup_database(password):
#     conn = get_db_connection(password)
#     initialize_schema(conn)
#     return conn


