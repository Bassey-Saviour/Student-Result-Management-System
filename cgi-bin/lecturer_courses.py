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
        
        # Authenticate lecturer
        cursor.execute("SELECT lecturer_id, password FROM lecturer WHERE first_name = %s", (username,))
        lecturer_row = cursor.fetchone()
        if not lecturer_row:
            print(json.dumps({"error": "Username not found"}))
            return
        
        # Verify password
        stored_hash = lecturer_row['password'].encode('utf-8')
        try:
            if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                print(json.dumps({"error": "Invalid password"}))
                return
        except Exception as e:
            print(json.dumps({"error": "Authentication failed"}))
            return
        
        lecturer_id = lecturer_row['lecturer_id']
        
        # Fetch courses for the lecturer
        query = (
            "SELECT c.course_id, c.course_code, c.course_title, c.credit_units "
            "FROM course c "
            "WHERE c.lecturer_id = %s "
            "ORDER BY c.course_code"
        )
        cursor.execute(query, (lecturer_id,))
        rows = cursor.fetchall()
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        return
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass

    courses = []
    for r in rows:
        courses.append({
            'course_id': r.get('course_id'),
            'course_code': r.get('course_code'),
            'course_title': r.get('course_title'),
            'credit_units': r.get('credit_units')
        })

    payload = {
        'lecturer_id': lecturer_id,
        'courses': courses,
        'count': len(courses)
    }

    print(json.dumps(payload))

if __name__ == '__main__':
    main()
