#!/usr/bin/env python3
"""
Flask Application for Student Result Management System
Converts CGI scripts to Flask routes for PythonAnywhere deployment
"""

from flask import Flask, request, jsonify, send_from_directory
import bcrypt
import json
import sys
import os

# Ensure we can import from the cgi-bin folder (hyphenated name can't be a module)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CGI_BIN_DIR = os.path.join(BASE_DIR, 'cgi-bin')
if CGI_BIN_DIR not in sys.path:
    sys.path.insert(0, CGI_BIN_DIR)

from db_config import get_connection

app = Flask(__name__, static_folder='public', static_url_path='')

# Enable debug mode for development
app.config['DEBUG'] = False

def log_error(message):
    """Log errors to stderr for debugging"""
    sys.stderr.write(f"ERROR: {message}\n")

def grade_points(grade):
    """Calculate grade points from letter grade"""
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

def score_to_grade(score):
    """Convert numeric score to letter grade"""
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

# Route to serve index.html at root
@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

# Route to serve static files from public directory
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('public', path)

# Student Results API
@app.route('/api/student_results', methods=['POST'])
def student_results():
    """Authenticate student and fetch their results"""
    data = request.get_json() if request.is_json else request.form
    matric = data.get('matricNo') or data.get('matric_no') or ''
    password = data.get('password') or ''

    if not matric or not password:
        return jsonify({"error": "missing matricNo or password"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Authenticate student
        cursor.execute("SELECT student_id, password FROM student WHERE matric_no = %s", (matric,))
        student_row = cursor.fetchone()
        if not student_row:
            return jsonify({"error": "Student not found"}), 404
        
        # Verify password
        stored_hash = student_row['password'].encode('utf-8')
        try:
            if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return jsonify({"error": "Invalid password"}), 401
        except Exception as e:
            return jsonify({"error": "Authentication failed"}), 500
        
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
        log_error(f"student_results error: {str(e)}")
        return jsonify({"error": str(e)}), 500
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

    return jsonify(payload)

# Lecturer Courses API
@app.route('/api/lecturer_courses', methods=['POST'])
def lecturer_courses():
    """Authenticate lecturer and fetch their courses"""
    data = request.get_json() if request.is_json else request.form
    username = data.get('username') or ''
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({"error": "missing username or password"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Authenticate lecturer
        cursor.execute("SELECT lecturer_id, password FROM lecturer WHERE first_name = %s", (username,))
        lecturer_row = cursor.fetchone()
        if not lecturer_row:
            return jsonify({"error": "Username not found"}), 404
        
        # Verify password
        stored_hash = lecturer_row['password'].encode('utf-8')
        try:
            if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return jsonify({"error": "Invalid password"}), 401
        except Exception as e:
            return jsonify({"error": "Authentication failed"}), 500
        
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
        log_error(f"lecturer_courses error: {str(e)}")
        return jsonify({"error": str(e)}), 500
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

    return jsonify(payload)

# Get Course Students API
@app.route('/api/get_course_students', methods=['GET', 'POST'])
def get_course_students():
    """Get all students enrolled in a course"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        course_id = data.get('course_id') or ''
    else:
        course_id = request.args.get('course_id') or ''

    if not course_id:
        return jsonify({"error": "missing course_id"}), 400

    try:
        course_id = int(course_id)
    except (ValueError, TypeError):
        return jsonify({"error": "invalid course_id"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Get course details
        cursor.execute("SELECT course_code, course_title, department_id FROM course WHERE course_id = %s", (course_id,))
        course_row = cursor.fetchone()
        if not course_row:
            return jsonify({"error": "Course not found"}), 404

        dept_id = course_row['department_id']

        # Get all students in the same department
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
        log_error(f"get_course_students error: {str(e)}")
        return jsonify({"error": str(e)}), 500
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

    return jsonify(payload)

# Upload Results API
@app.route('/api/upload_results', methods=['POST'])
def upload_results():
    """Upload or update a student's result for a course"""
    data = request.get_json() if request.is_json else request.form
    course_id = data.get('course_id') or ''
    student_id = data.get('student_id') or ''
    score = data.get('score') or ''

    # Validate inputs
    if not course_id or not student_id or not score:
        return jsonify({"error": "missing course_id, student_id, or score"}), 400

    try:
        course_id = int(course_id)
        student_id = int(student_id)
        score = int(score)
        if score < 0 or score > 100:
            raise ValueError("Score must be between 0 and 100")
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400

    grade = score_to_grade(score)

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Verify student exists
        cursor.execute("SELECT student_id FROM student WHERE student_id = %s", (student_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Student not found"}), 404

        # Verify course exists
        cursor.execute("SELECT course_id FROM course WHERE course_id = %s", (course_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Course not found"}), 404

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
        log_error(f"upload_results error: {str(e)}")
        return jsonify({"error": str(e)}), 500
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

    return jsonify(payload)

# Admin Login API
@app.route('/api/admin_login', methods=['POST'])
def admin_login():
    """Authenticate admin user"""
    data = request.get_json() if request.is_json else request.form
    username = data.get('username') or ''
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({"error": "missing username or password"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Authenticate admin
        cursor.execute("SELECT admin_id, password FROM admin WHERE username = %s", (username,))
        admin_row = cursor.fetchone()
        if not admin_row:
            return jsonify({"error": "Invalid username"}), 404
        
        # Verify password
        stored_hash = admin_row['password'].encode('utf-8')
        try:
            if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return jsonify({"error": "Invalid password"}), 401
        except Exception as e:
            return jsonify({"error": "Authentication failed"}), 500
        
        admin_id = admin_row['admin_id']
        
    except Exception as e:
        log_error(f"admin_login error: {str(e)}")
        return jsonify({"error": str(e)}), 500
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

    return jsonify(payload)

# Get All Data API (Admin)
@app.route('/api/get_all_data', methods=['GET', 'POST'])
def get_all_data():
    """Fetch all students, lecturers, or courses"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        action = data.get('action', '')
    else:
        action = request.args.get('action', '')
    
    response = {}
    
    try:
        if action == 'get_students':
            response['students'] = fetch_students()
        elif action == 'get_lecturers':
            response['lecturers'] = fetch_lecturers()
        elif action == 'get_courses':
            response['courses'] = fetch_courses()
        elif action == 'get_all':
            response['students'] = fetch_students()
            response['lecturers'] = fetch_lecturers()
            response['courses'] = fetch_courses()
        else:
            return jsonify({'error': 'Invalid action'}), 400
        
        return jsonify(response)
        
    except Exception as e:
        log_error(f"get_all_data error: {str(e)}")
        return jsonify({"error": str(e)}), 500

def fetch_students():
    """Fetch all students with their department information"""
    try:
        conn = get_connection()
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
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

def fetch_lecturers():
    """Fetch all lecturers with their department information"""
    try:
        conn = get_connection()
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
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

def fetch_courses():
    """Fetch all courses with lecturer and department information"""
    try:
        conn = get_connection()
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
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

# Add Data API (Admin)
@app.route('/api/add_data', methods=['POST'])
def add_data():
    """Add student, lecturer, or course"""
    data = request.get_json() if request.is_json else request.form
    action = data.get('action', '')
    
    response = {}
    
    try:
        if action == 'add_student':
            student_data = {
                'matric_no': data.get('matric_no'),
                'first_name': data.get('first_name'),
                'last_name': data.get('last_name'),
                'email': data.get('email'),
                'department_code': data.get('department_code'),
                'level': data.get('level', 400),
                'password': data.get('password', 'student123')
            }
            response = add_student(student_data)
            
        elif action == 'add_lecturer':
            lecturer_data = {
                'first_name': data.get('first_name'),
                'last_name': data.get('last_name'),
                'email': data.get('email'),
                'department_code': data.get('department_code'),
                'password': data.get('password', 'lecturer123')
            }
            response = add_lecturer(lecturer_data)
            
        elif action == 'add_course':
            course_data = {
                'course_code': data.get('course_code'),
                'course_title': data.get('course_title'),
                'credit_units': data.get('credit_units'),
                'department_code': data.get('department_code'),
                'lecturer_name': data.get('lecturer_name')
            }
            response = add_course(course_data)
        
        else:
            return jsonify({'success': False, 'error': 'Invalid action'}), 400

        return jsonify(response)
        
    except Exception as e:
        log_error(f"add_data error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

def add_student(data):
    """Add a new student to the database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get department_id from department_code
        cursor.execute("SELECT department_id FROM department WHERE department_code = %s", 
                      (data['department_code'],))
        dept_result = cursor.fetchone()
        
        if not dept_result:
            return {"success": False, "message": f"Invalid department code: {data['department_code']}"}
        
        dept_id = dept_result[0]
        
        # Hash password
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
        return {"success": False, "message": str(e)}
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

def add_lecturer(data):
    """Add a new lecturer to the database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get department_id from department_code
        cursor.execute("SELECT department_id FROM department WHERE department_code = %s", 
                      (data['department_code'],))
        dept_result = cursor.fetchone()
        
        if not dept_result:
            return {"success": False, "message": f"Invalid department code: {data['department_code']}"}
        
        dept_id = dept_result[0]
        
        # Hash password
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
        return {"success": False, "message": str(e)}
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

def add_course(data):
    """Add a new course to the database"""
    try:
        conn = get_connection()
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
        return {"success": False, "message": str(e)}
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

# Delete Data API (Admin)
@app.route('/api/delete_data', methods=['POST', 'DELETE'])
def delete_data():
    """Delete a student, lecturer, or course"""
    data = request.get_json() if request.is_json else request.form
    entity_type = data.get('type', '')
    entity_id = data.get('id', '')
    
    if not entity_type or not entity_id:
        return jsonify({"error": "Missing type or id"}), 400
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if entity_type == 'student':
            # Delete student's results first (foreign key constraint)
            cursor.execute("DELETE FROM result WHERE student_id = %s", (entity_id,))
            # Delete student
            cursor.execute("DELETE FROM student WHERE student_id = %s", (entity_id,))
            
        elif entity_type == 'lecturer':
            # Check if lecturer has courses assigned
            cursor.execute("SELECT COUNT(*) FROM course WHERE lecturer_id = %s", (entity_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                return jsonify({"error": "Cannot delete lecturer with assigned courses. Reassign courses first."}), 400
            # Delete lecturer
            cursor.execute("DELETE FROM lecturer WHERE lecturer_id = %s", (entity_id,))
            
        elif entity_type == 'course':
            # Delete course results first (foreign key constraint)
            cursor.execute("DELETE FROM result WHERE course_id = %s", (entity_id,))
            # Delete course
            cursor.execute("DELETE FROM course WHERE course_id = %s", (entity_id,))
            
        else:
            return jsonify({"error": "Invalid entity type"}), 400
        
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": f"{entity_type.capitalize()} deleted successfully"
        })
        
    except Exception as e:
        log_error(f"delete_data error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass

if __name__ == '__main__':
    # Run the Flask development server
    app.run(host='0.0.0.0', port=5000, debug=True)
