# Student Result Management System - Deployment Guide

---

## Deployment Option 1: Render.com (Recommended - Easiest)

### Prerequisites

- GitHub account with your repo pushed
- Render account (free at render.com)

### Step 1: Create MySQL Database on Render

1. Go to [render.com](https://render.com)
2. Click "New +" → "MySQL"
3. Choose:
   - **Name**: `srms-database`
   - **MySQL Version**: 8
   - **Region**: Choose closest to you
   - **Plan**: Free tier (or paid if needed)
4. Click "Create Database"
5. Wait for database to provision (~5 minutes)
6. Copy the connection details (Host, Username, Password, Database)

### Step 2: Push Your Code to GitHub

```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 3: Deploy Flask App on Render

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Fill in the form:
   - **Name**: `srms-app`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. Click "Create Web Service"

### Step 4: Set Environment Variables

1. Go to your web service dashboard
2. Click "Environment" in the left menu
3. Add these environment variables:
   ```
   DB_HOST=<your_mysql_host>
   DB_USER=<your_mysql_user>
   DB_PASSWORD=<your_mysql_password>
   DB_NAME=<your_mysql_database>
   ```
   (Get these from your Render MySQL database details)
4. Click "Save"

### Step 5: Deploy Your Database Schema

1. From your Render MySQL database page, click "Connect"
2. Copy the MySQL connection string
3. Import the schema locally:
   ```bash
   mysql -h <host> -u <user> -p < database/SRMS-copy.sql
   ```
   Enter your Render MySQL password when prompted

### Step 6: Access Your App

- Your app is live at `https://srms-app.render.com` (Render will give you the exact URL)

### Troubleshooting

- **"Connection refused"**: Check that environment variables match your database credentials
- **"Gunicorn not found"**: Add `gunicorn==21.2.0` to `requirements.txt`
- **"Database connection failed"**: Ensure your MySQL schema was imported successfully
- Check logs in Render dashboard under "Logs"

---

## Deployment Option 2: PythonAnywhere

- Zip your project folder and upload to PythonAnywhere.
- Unzip in your PythonAnywhere home directory (e.g., `/home/yourusername/Student-Result-Management-System`).

## 2. Set Up Virtual Environment

- Open a Bash console on PythonAnywhere.
- Run:
  ```bash
  cd ~/Student-Result-Management-System
  python3.10 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

## 3. Configure MySQL Database

- Ensure your MySQL database is set up on PythonAnywhere.
- Update `cgi-bin/db_config.py` with your PythonAnywhere MySQL credentials.

## 4. Configure Web App

- Go to the PythonAnywhere Web tab.
- Set the **Source code** path to your project directory.
- Set the **WSGI configuration file** to `/home/yourusername/Student-Result-Management-System/wsgi.py`.
- Set **Working directory** to your project directory.
- Set **Virtualenv** to `/home/yourusername/Student-Result-Management-System/venv`.

## 5. Static Files

- Add a static file mapping:
  - **URL**: `/static/` → **Directory**: `/home/yourusername/Student-Result-Management-System/public/`

## 6. Reload Web App

- Click **Reload** on the PythonAnywhere Web tab.

## 7. Access Your App

- Visit `https://yourusername.pythonanywhere.com/`

## Troubleshooting

- Check error logs in the PythonAnywhere Web tab.
- Ensure all dependencies are installed in your virtualenv.
- Make sure your database credentials are correct.

---

For more help, see the PythonAnywhere help pages or ask for support.
