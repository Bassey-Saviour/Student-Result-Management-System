# Student Result Management System (SRMS)

A web-based system for managing student results in a school, built for COSC 333 / ITGY 401.

## Features

- **Student Portal**: Students can log in with matric number and password to view their results and GPA
- **Lecturer Portal**: Lecturers can log in to view assigned courses and upload/update student scores in bulk
- **Admin Dashboard**: Manage students, lecturers, and courses
- **Secure Authentication**: Password hashing with bcrypt
- **Auto Grade Calculation**: Grades are automatically calculated from scores

## Project Structure

```
student_result_management_system/
│
├── public/                     # Frontend HTML files
│   ├── index.html             # Landing page
│   ├── student.html           # Student results view
│   ├── lecturer.html          # Lecturer grade upload
│   ├── admin.html             # Admin management dashboard
│   └── css/
│       └── styles.css         # Styling
│
├── cgi-bin/                    # Backend CGI scripts
│   ├── db_config.py           # Database configuration
│   ├── student_results.py     # Fetch student results
│   ├── lecturer_courses.py    # Lecturer authentication & courses
│   ├── get_course_students.py # Get students in a course
│   ├── upload_results_by_student.py  # Batch upload results
│   ├── get_all_data.py        # Admin: fetch all data
│   └── add_data.py            # Admin: add students/lecturers/courses
│
├── database/
│   ├── SRMS-copy.sql          # Database schema and sample data
│   └── erd.png
│
└── README.md
```

## Prerequisites

- **Python 3.7+**
- **MySQL 8.0+** (or MariaDB)
- **pip** (Python package installer)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Bassey-Saviour/Student-Result-Management-System.git
cd Student-Result-Management-System
```

### 2. Install Python Dependencies

```bash
pip install mysql-connector-python bcrypt
```

Or if using `pip3`:

```bash
pip3 install mysql-connector-python bcrypt
```

### 3. Set Up MySQL Database

1. **Start MySQL server** (if not already running)

2. **Create the database and import schema:**

```bash
mysql -u root -p < database/SRMS-copy.sql
```

Or manually in MySQL:

```sql
mysql -u root -p
source /path/to/database/SRMS-copy.sql;
```

3. **Configure database credentials:**

Edit `cgi-bin/db_config.py` and update with your MySQL credentials:

```python
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="your_mysql_username",      # Change this
        password="your_mysql_password",  # Change this
        database="result copy"
    )
```

### 4. Start the CGI Server

From the project root directory:

```bash
python -m http.server --cgi 8000
```

Or on some systems:

```bash
python3 -m http.server --cgi 8000
```

### 5. Access the Application

Open your browser and navigate to:

```
http://localhost:8000/public/index.html
```

## Default Login Credentials

### Students

- **Matric Number**: `22/0001`
- **Password**: test123
- **Matric Number**: `22/0002`
- **Password**: test124
- **Matric Number**: `22/0003`
- **Password**: test125
- **Matric Number**: `22/0004`
- **Password**: test126
- **Matric Number**: `22/0010`
- **Password**: test127
- **Matric Number**: `22/0005`
- **Password**: test128

### Lecturers

- **Username**: `Seun` (first name)
- **Password**: lect123
- **Username**: `Dondada` (first name)
- **Password**: lect124
- **Username**: `Amina` (first name)
- **Password**: lect125
- **Username**: `Famudims` (first name)
- **Password**: lect126
- **Username**: `Ajayi` (first name)
- **Password**: lect127

### Sample Data

The SQL file includes sample students, lecturers, courses, and results for testing.

## Grading Scale

- **A**: 80-100
- **B**: 60-79
- **C**: 50-59
- **D**: 45-49
- **E**: 40-45
- **F**: 0-39

## Troubleshooting

### CSS/JavaScript Not Updating

- Hard refresh: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
- Open DevTools (F12) and disable cache in Settings

### Database Connection Errors

- Verify MySQL is running: `mysql -u root -p`
- Check credentials in `cgi-bin/db_config.py`
- Ensure database `result copy` exists

### CGI Scripts Not Executing

- Ensure scripts have proper permissions (Unix/Linux/Mac):
  ```bash
  chmod +x cgi-bin/*.py
  ```
- Verify Python shebang in scripts: `#!/usr/bin/env python3`

## Technologies Used

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Python 3 (CGI)
- **Database**: MySQL 8.0
- **Security**: bcrypt for password hashing

## Contributors

CIS, CS group 11

## License

This project is for educational purposes (COSC 333 / ITGY 401).
