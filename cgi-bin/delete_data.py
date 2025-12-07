#!/usr/bin/env python3
"""
Delete Data CGI Script
Handles deletion of students, lecturers, and courses
"""

import cgi
import json
import sys
from db_config import get_connection


def delete_data():
    """Delete a student, lecturer, or course"""
    # Parse form data
    form = cgi.FieldStorage()
    
    try:
        # Get JSON data if available, otherwise from form
        if 'CONTENT_TYPE' in sys.environ and 'application/json' in sys.environ['CONTENT_TYPE']:
            import io
            body = io.TextIOWrapper(sys.stdin, encoding='utf-8')
            data = json.load(body)
        else:
            data = {
                'type': form.getvalue('type', ''),
                'id': form.getvalue('id', '')
            }
        
        entity_type = data.get('type', '')
        entity_id = data.get('id', '')
        
        if not entity_type or not entity_id:
            return {'error': 'Missing type or id'}, 400
        
        try:
            entity_id = int(entity_id)
        except (ValueError, TypeError):
            return {'error': 'Invalid entity ID'}, 400
        
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
                return {'error': 'Cannot delete lecturer with assigned courses. Reassign courses first.'}, 400
            # Delete lecturer
            cursor.execute("DELETE FROM lecturer WHERE lecturer_id = %s", (entity_id,))
            
        elif entity_type == 'course':
            # Delete course results first (foreign key constraint)
            cursor.execute("DELETE FROM result WHERE course_id = %s", (entity_id,))
            # Delete course
            cursor.execute("DELETE FROM course WHERE course_id = %s", (entity_id,))
            
        else:
            return {'error': 'Invalid entity type'}, 400
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'message': f'{entity_type.capitalize()} deleted successfully'
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500


if __name__ == '__main__':
    # Set content type
    print('Content-Type: application/json')
    
    result, status_code = delete_data()
    
    # Print status code as a comment (not standard but informative)
    print(f'Status: {status_code}')
    print()
    
    print(json.dumps(result))
