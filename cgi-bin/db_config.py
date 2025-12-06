import mysql.connector
import os

def get_connection():
    # Get database credentials from environment variables
    # For local development, uses defaults; for Render, uses env vars
    host = os.getenv('DB_HOST', '')
    user = os.getenv('DB_USER', '')
    password = os.getenv('DB_PASSWORD', '')
    database = os.getenv('DB_NAME', '')
    
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
