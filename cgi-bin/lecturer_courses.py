#!/usr/bin/env python3
import cgi
import cgitb
import json
from db_config import get_connection

cgitb.enable()

def main():
    form = cgi.FieldStorage()
    lecturer_id = form.getfirst('lecturer_id') or ''
    lecturer_email = form.getfirst('lecturer_email') or ''

    print("Content-Type: application/json")
    print()

    if not lecturer_id and not lecturer_email:
        print(json.dumps({"error": "missing lecturer_id or lecturer_email"}))
        return

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Fetch courses for the lecturer
        if lecturer_id:
            query = (
                "SELECT c.course_id, c.course_code, c.course_title, c.credit_units "
                "FROM course c "
                "WHERE c.lecturer_id = %s "
                "ORDER BY c.course_code"
            )
            cursor.execute(query, (int(lecturer_id),))
        else:
            query = (
                "SELECT c.course_id, c.course_code, c.course_title, c.credit_units "
                "FROM course c "
                "JOIN lecturer l ON c.lecturer_id = l.lecturer_id "
                "WHERE l.email = %s "
                "ORDER BY c.course_code"
            )
            cursor.execute(query, (lecturer_email,))
        
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
        'lecturer_id': lecturer_id if lecturer_id else None,
        'lecturer_email': lecturer_email if lecturer_email else None,
        'courses': courses,
        'count': len(courses)
    }

    print(json.dumps(payload))

if __name__ == '__main__':
    main()
