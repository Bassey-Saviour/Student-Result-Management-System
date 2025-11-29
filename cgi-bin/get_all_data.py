#!/usr/bin/env python3
import cgi
import cgitb
from db_config import get_connection
import json
import sys

# Enable CGI error reporting
cgitb.enable()

# Add error logging
def log_error(message):
    """Log errors to stderr for debugging"""
    sys.stderr.write(f"ERROR: {message}\n")

def get_students():
    """Fetch all students with their department information"""
    try:
        conn = get_connection()
        if not conn:
            return []
        
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT s.student_id, s.matric_no, s.first_name, s.last_name, 
                   s.email, d.department_code
            FROM student s
            JOIN department d ON s.department_id = d.department_id
            ORDER BY s.matric_no
        """
        cursor.execute(query)
        students = cursor.fetchall()
        return students
    except Exception as e:
        log_error(f"get_students error: {str(e)}")
        return []
    finally:
        try:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        except:
            pass

def get_lecturers():
    """Fetch all lecturers with their department information"""
    try:
        conn = get_connection()
        if not conn:
            return []
        
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT l.lecturer_id, l.first_name, l.last_name, 
                   l.email, d.department_code
            FROM lecturer l
            JOIN department d ON l.department_id = d.department_id
            ORDER BY l.first_name
        """
        cursor.execute(query)
        lecturers = cursor.fetchall()
        return lecturers
    except Exception as e:
        log_error(f"get_lecturers error: {str(e)}")
        return []
    finally:
        try:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        except:
            pass

def get_courses():
    """Fetch all courses with lecturer and department information"""
    try:
        conn = get_connection()
        if not conn:
            return []
        
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT c.course_id, c.course_code, c.course_title, 
                   c.credit_units, d.department_code,
                   CONCAT(l.first_name, ' ', l.last_name) as lecturer_name
            FROM course c
            JOIN department d ON c.department_id = d.department_id
            JOIN lecturer l ON c.lecturer_id = l.lecturer_id
            ORDER BY c.course_code
        """
        cursor.execute(query)
        courses = cursor.fetchall()
        return courses
    except Exception as e:
        log_error(f"get_courses error: {str(e)}")
        return []
    finally:
        try:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        except:
            pass

def main():
    """Main function to handle CGI requests"""
    try:
        # Print HTTP headers
        print("Content-Type: application/json")
        print()
        
        # Get form data
        form = cgi.FieldStorage()
        action = form.getvalue('action', '')
        
        response = {}
        
        if action == 'get_students':
            response['students'] = get_students()
        elif action == 'get_lecturers':
            response['lecturers'] = get_lecturers()
        elif action == 'get_courses':
            response['courses'] = get_courses()
        elif action == 'get_all':
            response['students'] = get_students()
            response['lecturers'] = get_lecturers()
            response['courses'] = get_courses()
        else:
            response['error'] = 'Invalid action'
        
        # Output JSON response
        print(json.dumps(response, default=str))
        
    except Exception as e:
        log_error(f"main error: {str(e)}")
        print(json.dumps({"error": str(e)}, default=str))

if __name__ == '__main__':
    main()