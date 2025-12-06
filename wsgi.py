"""
WSGI configuration for PythonAnywhere deployment
This file should be used in your PythonAnywhere web app configuration
"""

import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/Student-Result-Management-System'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set the path to the cgi-bin directory for imports
cgi_bin_path = os.path.join(project_home, 'cgi-bin')
if cgi_bin_path not in sys.path:
    sys.path.insert(0, cgi_bin_path)

# Import the Flask app
from app import app as application
