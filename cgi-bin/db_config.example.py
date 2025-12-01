#!/usr/bin/env python3
"""
Database configuration template.
Copy this file to db_config.py and update with your credentials.
"""
import mysql.connector

def get_connection():
    """
    Returns a connection to the MySQL database.
    """
    return mysql.connector.connect(
        host="localhost",
        user="your_mysql_username",      # UPDATE THIS
        password="your_mysql_password",  # UPDATE THIS
        database="result copy"
    )