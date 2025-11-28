#!/usr/bin/env python3
import cgi
import cgitb
import json
from db_config import get_connection

cgitb.enable()

def score_to_grade(score):
    """Convert numeric score to letter grade."""
    try:
        s = int(score)
    except (ValueError, TypeError):
        return None
    
    if s >= 90:
        return 'A'
    elif s >= 80:
        return 'B'
    elif s >= 70:
        return 'C'
    elif s >= 60:
        return 'D'
    elif s >= 50:
        return 'E'
    else:
        return 'F'

def main():
    form = cgi.FieldStorage()
    course_id = form.getfirst('course_id') or ''
    matric_no = form.getfirst('matric_no') or ''
    score = form.getfirst('score') or ''

    print("Content-Type: application/json")
    print()

    # Validate inputs
    if not course_id or not matric_no or not score:
        print(json.dumps({"error": "missing course_id, matric_no, or score"}))
        return

    try:
        course_id = int(course_id)
        score = int(score)
        if score < 0 or score > 100:
            raise ValueError("Score must be between 0 and 100")
    except (ValueError, TypeError) as e:
        print(json.dumps({"error": str(e)}))
        return

    grade = score_to_grade(score)

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Find student by matric_no
        cursor.execute("SELECT student_id, department_id FROM student WHERE matric_no = %s", (matric_no,))
        student_row = cursor.fetchone()
        if not student_row:
            print(json.dumps({"error": "Student not found"}))
            return

        student_id = student_row['student_id']
        student_dept = student_row['department_id']

        # Verify the course exists and get its department
        cursor.execute("SELECT course_id, department_id FROM course WHERE course_id = %s", (course_id,))
        course_row = cursor.fetchone()
        if not course_row:
            print(json.dumps({"error": "Course not found"}))
            return

        course_dept = course_row['department_id']

        # Check if student's department matches course department (basic enrollment validation)
        if student_dept != course_dept:
            print(json.dumps({"error": "Student is not enrolled in this course (department mismatch)"}))
            return

        # Insert or update result
        try:
            cursor.execute(
                "INSERT INTO result (student_id, course_id, score, grade) "
                "VALUES (%s, %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE score = %s, grade = %s",
                (student_id, course_id, score, grade, score, grade)
            )
            conn.commit()
            success = True
        except Exception as e:
            conn.rollback()
            raise e

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
        'message': 'Result uploaded successfully',
        'matric_no': matric_no,
        'course_id': course_id,
        'score': score,
        'grade': grade
    }

    print(json.dumps(payload))

if __name__ == '__main__':
    main()
