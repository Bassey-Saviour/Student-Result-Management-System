#!/usr/bin/env python3
import cgi
import cgitb
import json
from db_config import get_connection

cgitb.enable()

def main():
    form = cgi.FieldStorage()
    course_id = form.getfirst('course_id') or ''

    print("Content-Type: application/json")
    print()

    if not course_id:
        print(json.dumps({"error": "missing course_id"}))
        return

    try:
        course_id = int(course_id)
    except (ValueError, TypeError):
        print(json.dumps({"error": "invalid course_id"}))
        return

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Get course details
        cursor.execute("SELECT course_code, course_title, department_id FROM course WHERE course_id = %s", (course_id,))
        course_row = cursor.fetchone()
        if not course_row:
            print(json.dumps({"error": "Course not found"}))
            return

        dept_id = course_row['department_id']

        # Get all students in the same department (enrolled in this course)
        query = (
            "SELECT DISTINCT s.student_id, s.matric_no, s.first_name, s.last_name, "
            "r.score, r.grade "
            "FROM student s "
            "LEFT JOIN result r ON s.student_id = r.student_id AND r.course_id = %s "
            "WHERE s.department_id = %s "
            "ORDER BY s.matric_no"
        )
        cursor.execute(query, (course_id, dept_id))
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

    students = []
    for r in rows:
        score = r.get('score')
        grade = r.get('grade') or ''
        students.append({
            'student_id': r.get('student_id'),
            'matric_no': r.get('matric_no'),
            'first_name': r.get('first_name'),
            'last_name': r.get('last_name'),
            'score': score,
            'grade': grade
        })

    payload = {
        'course_id': course_id,
        'course_code': course_row['course_code'],
        'course_title': course_row['course_title'],
        'students': students,
        'count': len(students)
    }

    print(json.dumps(payload))

if __name__ == '__main__':
    main()
