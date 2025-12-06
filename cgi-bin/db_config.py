import mysql.connector
import os

def get_connection():
    # Get database credentials from environment variables
    # For local development, uses defaults; for Render/Aiven, uses env vars
    host = os.getenv('DB_HOST', '')
    user = os.getenv('DB_USER', '')
    password = os.getenv('DB_PASSWORD', '')
    database = os.getenv('DB_NAME', '')
    port = int(os.getenv('DB_PORT', ''))  # Default MySQL port is 3306
    
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port
    )
