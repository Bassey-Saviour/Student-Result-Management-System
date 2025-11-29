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

def add_student(data):
    """Add a new student to the database"""
    try:
        conn = get_connection()
        if not conn:
            return {"success": False, "message": "Database connection failed"}
        
        cursor = conn.cursor()
        
        # Get department_id from department_code
        cursor.execute("SELECT department_id FROM department WHERE department_code = %s", 
                      (data['department_code'],))
        dept_result = cursor.fetchone()
        
        if not dept_result:
            return {"success": False, "message": f"Invalid department code: {data['department_code']}"}
        
        dept_id = dept_result[0]
        
        # Hash password
        import bcrypt
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        query = """
            INSERT INTO student (matric_no, first_name, last_name, email, level, department_id, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['matric_no'],
            data['first_name'],
            data['last_name'],
            data['email'],
            data.get('level', 400),
            dept_id,
            hashed_password
        ))
        
        conn.commit()
        return {"success": True, "message": "Student added successfully"}
        
    except Exception as e:
        log_error(f"add_student error: {str(e)}")
        return {"success": False, "message": str(e)}
    finally:
        try:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        except:
            pass

def add_lecturer(data):
    """Add a new lecturer to the database"""
    try:
        conn = get_connection()
        if not conn:
            return {"success": False, "message": "Database connection failed"}
        
        cursor = conn.cursor()
        
        # Get department_id from department_code
        cursor.execute("SELECT department_id FROM department WHERE department_code = %s", 
                      (data['department_code'],))
        dept_result = cursor.fetchone()
        
        if not dept_result:
            return {"success": False, "message": f"Invalid department code: {data['department_code']}"}
        
        dept_id = dept_result[0]
        
        # Hash password
        import bcrypt
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        query = """
            INSERT INTO lecturer (first_name, last_name, email, department_id, password)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['first_name'],
            data['last_name'],
            data['email'],
            dept_id,
            hashed_password
        ))
        
        conn.commit()
        return {"success": True, "message": "Lecturer added successfully"}
        
    except Exception as e:
        log_error(f"add_lecturer error: {str(e)}")
        return {"success": False, "message": str(e)}
    finally:
        try:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        except:
            pass

def add_course(data):
    """Add a new course to the database"""
    try:
        conn = get_connection()
        if not conn:
            return {"success": False, "message": "Database connection failed"}
        
        cursor = conn.cursor()
        
        # Get department_id from department_code
        cursor.execute("SELECT department_id FROM department WHERE department_code = %s", 
                      (data['department_code'],))
        dept_result = cursor.fetchone()
        
        if not dept_result:
            return {"success": False, "message": f"Invalid department code: {data['department_code']}"}
        
        dept_id = dept_result[0]
        
        # Get lecturer_id from first name
        cursor.execute("SELECT lecturer_id FROM lecturer WHERE first_name = %s", 
                      (data['lecturer_name'],))
        lect_result = cursor.fetchone()
        
        if not lect_result:
            return {"success": False, "message": f"Lecturer '{data['lecturer_name']}' not found"}
        
        lect_id = lect_result[0]
        
        query = """
            INSERT INTO course (course_code, course_title, credit_units, department_id, lecturer_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['course_code'],
            data['course_title'],
            data['credit_units'],
            dept_id,
            lect_id
        ))
        
        conn.commit()
        return {"success": True, "message": "Course added successfully"}
        
    except Exception as e:
        log_error(f"add_course error: {str(e)}")
        return {"success": False, "message": str(e)}
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
        
        log_error("Script started")

        # Get form data
        form = cgi.FieldStorage()
        action = form.getvalue('action', '')
        log_error(f"Action received: {action}")
        
        response = {}

        if action == 'add_student':
            data = {
                'matric_no': form.getvalue('matric_no'),
                'first_name': form.getvalue('first_name'),
                'last_name': form.getvalue('last_name'),
                'email': form.getvalue('email'),
                'department_code': form.getvalue('department_code'),
                'level': form.getvalue('level', 400),
                'password': form.getvalue('password', 'student123')
            }
            log_error(f"Adding student: {data['matric_no']}")
            response = add_student(data)
            
        elif action == 'add_lecturer':
            data = {
                'first_name': form.getvalue('first_name'),
                'last_name': form.getvalue('last_name'),
                'email': form.getvalue('email'),
                'department_code': form.getvalue('department_code'),
                'password': form.getvalue('password', 'lecturer123')
            }
            log_error(f"Adding lecturer: {data['email']}")
            response = add_lecturer(data)
            
        elif action == 'add_course':
            data = {
                'course_code': form.getvalue('course_code'),
                'course_title': form.getvalue('course_title'),
                'credit_units': form.getvalue('credit_units'),
                'department_code': form.getvalue('department_code'),
                'lecturer_name': form.getvalue('lecturer_name')
            }
            log_error(f"Adding course: {data['course_code']}")
            response = add_course(data)
        
        else:
            response = {'success': False, 'error': 'Invalid action', 'action_received': action}

        # Output JSON response
        log_error(f"Sending response: {json.dumps(response, default=str)[:100]}")
        print(json.dumps(response, default=str))
        
    except Exception as e:
        log_error(f"main error: {str(e)}")
        error_response = {"success": False, "error": str(e), "type": "exception"}
        print(json.dumps(error_response, default=str))

if __name__ == '__main__':
    main()