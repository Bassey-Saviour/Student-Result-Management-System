#!/usr/bin/env python3
import cgi
import cgitb
import json
import bcrypt
from db_config import get_connection

cgitb.enable()

def main():
    form = cgi.FieldStorage()
    username = form.getfirst('username') or ''
    password = form.getfirst('password') or ''

    print("Content-Type: application/json")
    print()

    if not username or not password:
        print(json.dumps({"error": "missing username or password"}))
        return

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Authenticate admin
        cursor.execute("SELECT admin_id, password FROM admin WHERE username = %s", (username,))
        admin_row = cursor.fetchone()
        if not admin_row:
            print(json.dumps({"error": "Invalid username"}))
            return
        
        # Verify password
        stored_hash = admin_row['password'].encode('utf-8')
        try:
            if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                print(json.dumps({"error": "Invalid password"}))
                return
        except Exception as e:
            print(json.dumps({"error": "Authentication failed"}))
            return
        
        admin_id = admin_row['admin_id']
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        return
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass

    payload = {
        'success': True,
        'admin_id': admin_id,
        'username': username
    }

    print(json.dumps(payload))

if __name__ == '__main__':
    main()
