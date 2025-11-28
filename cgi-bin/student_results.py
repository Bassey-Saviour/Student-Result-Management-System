#!/usr/bin/env python3
import cgi
import cgitb
import json
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

    print("Content-Type: application/json")
    print()

    if not matric:
        print(json.dumps({"error": "missing matricNo"}))
        return

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = (
            "SELECT c.course_code, c.course_title, c.credit_units, r.score, r.grade "
            "FROM student s "
            "JOIN result r ON s.student_id = r.student_id "
            "JOIN course c ON r.course_id = c.course_id "
            "WHERE s.matric_no = %s "
            "ORDER BY c.course_code"
        )
        cursor.execute(query, (matric,))
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
