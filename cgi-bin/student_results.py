#!/usr/bin/env python3
import cgi
import cgitb
import json
import bcrypt
from db_config import get_connection

cgitb.enable()

def grade_points(grade):
    if not grade:
        return 0
    g = grade.strip().upper()
    if 'A' in g:
        return 5
    if 'B' in g:
        return 4
    if 'C' in g:
        return 3
    if 'D' in g:
        return 2
    if 'E' in g:
        return 1
    return 0

def main():
    form = cgi.FieldStorage()
    matric = form.getfirst('matricNo') or form.getfirst('matric_no') or ''
    password = form.getfirst('password') or ''

    print("Content-Type: application/json")
    print()

    if not matric or not password:
        print(json.dumps({"error": "missing matricNo or password"}))
        return

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Authenticate student
        cursor.execute("SELECT student_id, password FROM student WHERE matric_no = %s", (matric,))
        student_row = cursor.fetchone()
        if not student_row:
            print(json.dumps({"error": "Student not found"}))
            return
        
        # Verify password
        stored_hash = student_row['password'].encode('utf-8')
        try:
            if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                print(json.dumps({"error": "Invalid password"}))
                return
        except Exception as e:
            print(json.dumps({"error": "Authentication failed"}))
            return
        
        student_id = student_row['student_id']
        
        # Fetch results
        query = (
            "SELECT c.course_code, c.course_title, c.credit_units, r.score, r.grade "
            "FROM result r "
            "JOIN course c ON r.course_id = c.course_id "
            "WHERE r.student_id = %s "
            "ORDER BY c.course_code"
        )
        cursor.execute(query, (student_id,))
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

    results = []
    total_points = 0
    total_units = 0
    for r in rows:
        cu = r.get('credit_units') or 0
        gp = grade_points(r.get('grade'))
        total_points += gp * cu
        total_units += cu
        results.append({
            'course_code': r.get('course_code'),
            'course_title': r.get('course_title'),
            'credit_units': cu,
            'score': r.get('score'),
            'grade': r.get('grade')
        })

    gpa = round((total_points / total_units), 2) if total_units > 0 else None

    payload = {
        'matric_no': matric,
        'results': results,
        'gpa': gpa,
        'count': len(results)
    }

    print(json.dumps(payload))

if __name__ == '__main__':
    main()
