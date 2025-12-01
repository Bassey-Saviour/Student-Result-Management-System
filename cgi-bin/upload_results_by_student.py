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
    
    if s >= 80:
        return 'A'
    elif s >= 60:
        return 'B'
    elif s >= 50:
        return 'C'
    elif s >= 45:
        return 'D'
    elif s >= 40:
        return 'E'
    else:
        return 'F'

def main():
    form = cgi.FieldStorage()
    course_id = form.getfirst('course_id') or ''
    student_id = form.getfirst('student_id') or ''
    score = form.getfirst('score') or ''

    print("Content-Type: application/json")
    print()

    # Validate inputs
    if not course_id or not student_id or not score:
        print(json.dumps({"error": "missing course_id, student_id, or score"}))
        return

    try:
        course_id = int(course_id)
        student_id = int(student_id)
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

        # Verify student exists
        cursor.execute("SELECT student_id FROM student WHERE student_id = %s", (student_id,))
        if not cursor.fetchone():
            print(json.dumps({"error": "Student not found"}))
            return

        # Verify course exists
        cursor.execute("SELECT course_id FROM course WHERE course_id = %s", (course_id,))
        if not cursor.fetchone():
            print(json.dumps({"error": "Course not found"}))
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
        'student_id': student_id,
        'course_id': course_id,
        'score': score,
        'grade': grade
    }

    print(json.dumps(payload))

if __name__ == '__main__':
    main()
