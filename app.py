import os
import sys
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash

# Configure templates and database paths for PyInstaller packaging support
if getattr(sys, 'frozen', False):
    # Running as a compiled PyInstaller standalone executable
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
    # Write SQLite database next to the .exe file (sys.executable) instead of inside temp folders
    DATABASE = os.path.join(os.path.dirname(sys.executable), "faculty.db")
else:
    # Running as normal python script
    app = Flask(__name__)
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "faculty.db")

app.secret_key = "super_secret_key" # Used for securing session cookies

def get_db():
    """Helper function to connect to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # Enables column access by name (e.g. row['name'])
    return conn

def init_db():
    """Initializes the database, creating tables if they do not exist."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create the teachers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            designation TEXT NOT NULL,
            phone_no TEXT NOT NULL,
            salary REAL NOT NULL,
            class INTEGER NOT NULL,
            address TEXT NOT NULL,
            pancard_no TEXT NOT NULL,
            aadhar_no TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    # Create the password table for the admin password
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password (
            id INTEGER PRIMARY KEY,
            pass TEXT NOT NULL
        )
    """)
    
    # Set default admin password 'admin123' if the password table is empty
    cursor.execute("SELECT * FROM password WHERE id = 1")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO password (id, pass) VALUES (1, 'admin123')")
    
    conn.commit()
    conn.close()

# Run table creation check on startup
init_db()

@app.route("/")
def index():
    """Redirects user to dashboard if logged in, otherwise to login page."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles admin and teacher logins."""
    if request.method == "POST":
        role = request.form.get("role")
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        
        conn = get_db()
        cursor = conn.cursor()
        
        if role == "admin":
            if username == "admin":
                cursor.execute("SELECT pass FROM password WHERE id = 1")
                row = cursor.fetchone()
                if row and row["pass"] == password:
                    session["user_id"] = "admin"
                    session["role"] = "admin"
                    conn.close()
                    return redirect(url_for("dashboard"))
            flash("Incorrect Admin Credentials!")
        elif role == "teacher":
            # Teachers log in using their Database ID as the username
            cursor.execute("SELECT * FROM teachers WHERE id = ? AND password = ?", (username, password))
            row = cursor.fetchone()
            if row:
                session["user_id"] = row["id"]
                session["role"] = "teacher"
                conn.close()
                return redirect(url_for("dashboard"))
            flash("Incorrect Teacher ID or Password!")
            
        conn.close()
        
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    """Displays dashboard based on user role (Admin lists all, Teacher views profile)."""
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    role = session["role"]
    conn = get_db()
    cursor = conn.cursor()
    
    if role == "admin":
        # Admin gets a list of all teachers
        cursor.execute("SELECT * FROM teachers")
        teachers = cursor.fetchall()
        
        # Admin gets the current admin password (for update form)
        cursor.execute("SELECT pass FROM password WHERE id = 1")
        admin_pass = cursor.fetchone()["pass"]
        conn.close()
        return render_template("dashboard.html", role=role, teachers=teachers, admin_pass=admin_pass)
    else:
        # Teacher gets their own profile details
        teacher_id = session["user_id"]
        cursor.execute("SELECT * FROM teachers WHERE id = ?", (teacher_id,))
        teacher = cursor.fetchone()
        conn.close()
        return render_template("dashboard.html", role=role, teacher=teacher)

@app.route("/add", methods=["POST"])
def add_teacher():
    """Allows Admin to add a new teacher record."""
    if session.get("role") != "admin":
        return "Unauthorized", 403
        
    name = request.form.get("name")
    designation = request.form.get("designation")
    phone_no = request.form.get("phone_no")
    salary = float(request.form.get("salary"))
    class_assigned = int(request.form.get("class"))
    address = request.form.get("address")
    pancard_no = request.form.get("pancard_no")
    aadhar_no = request.form.get("aadhar_no")
    password = request.form.get("password")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO teachers (name, designation, phone_no, salary, class, address, pancard_no, aadhar_no, password)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, designation, phone_no, salary, class_assigned, address, pancard_no, aadhar_no, password))
    conn.commit()
    conn.close()
    
    flash("Teacher added successfully!")
    return redirect(url_for("dashboard"))

@app.route("/update/<int:teacher_id>", methods=["POST"])
def update_teacher(teacher_id):
    """Allows Admin to update a teacher record."""
    if session.get("role") != "admin":
        return "Unauthorized", 403
        
    name = request.form.get("name")
    designation = request.form.get("designation")
    phone_no = request.form.get("phone_no")
    salary = float(request.form.get("salary"))
    class_assigned = int(request.form.get("class"))
    address = request.form.get("address")
    pancard_no = request.form.get("pancard_no")
    aadhar_no = request.form.get("aadhar_no")
    password = request.form.get("password")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE teachers 
        SET name=?, designation=?, phone_no=?, salary=?, class=?, address=?, pancard_no=?, aadhar_no=?, password=?
        WHERE id=?
    """, (name, designation, phone_no, salary, class_assigned, address, pancard_no, aadhar_no, password, teacher_id))
    conn.commit()
    conn.close()
    
    flash("Teacher details updated successfully!")
    return redirect(url_for("dashboard"))

@app.route("/delete/<int:teacher_id>", methods=["POST", "GET"])
def delete_teacher(teacher_id):
    """Allows Admin to delete a teacher record."""
    if session.get("role") != "admin":
        return "Unauthorized", 403
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
    conn.commit()
    conn.close()
    
    flash("Teacher deleted successfully!")
    return redirect(url_for("dashboard"))

@app.route("/change_admin_password", methods=["POST"])
def change_admin_password():
    """Allows Admin to update their dashboard login password."""
    if session.get("role") != "admin":
        return "Unauthorized", 403
        
    new_password = request.form.get("new_password")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE password SET pass = ? WHERE id = 1", (new_password,))
    conn.commit()
    conn.close()
    
    flash("Admin password updated successfully!")
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    """Clears session and redirects to login."""
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
