from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

# ================= APP =================
app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)
app.secret_key = "attendance_secret_key"

# ================= PATH SETUP =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "database.db")

# ================= DATABASE HELPER =================
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ================= LOGIN PAGE =================
@app.route("/", methods=["GET"])
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT username FROM teachers")
    teachers = [row["username"] for row in cur.fetchall()]
    conn.close()

    return render_template("index.html", teachers=teachers)

# ================= LOGIN HANDLER =================
@app.route("/login", methods=["POST"])
def login():
    role = request.form.get("role")
    username = request.form.get("email")
    password = request.form.get("password")

    conn = get_db_connection()
    cur = conn.cursor()

    # -------- TEACHER LOGIN --------
    if role == "Teacher":
        cur.execute(
            "SELECT teacher_id FROM teachers WHERE username=? AND password=?",
            (username, password)
        )
        teacher = cur.fetchone()
        conn.close()

        if teacher:
            session["role"] = "Teacher"
            session["teacher_id"] = teacher["teacher_id"]
            session["username"] = username
            return redirect(url_for("dashboard"))

    # -------- ADMIN LOGIN --------
    if role == "Admin":
        conn.close()
        if username == "Admin" and password == "admin":
            session["role"] = "Admin"
            return redirect(url_for("admin_dashboard"))

    return redirect(url_for("index"))

# ================= READ ATTENDANCE =================
def read_attendance_by_teacher(teacher_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            a.class_date,
            a.class_time,
            a.class_period,
            a.class_subject,
            s.student_id,
            s.full_name,
            s.grade_level
        FROM attendance_log a
        JOIN students s ON a.student_id = s.student_id
        WHERE a.teacher_id = ?
        ORDER BY a.class_date DESC, a.class_time DESC
    """, (teacher_id,))

    records = cur.fetchall()
    conn.close()
    return records

# ================= TEACHER DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if session.get("role") != "Teacher":
        return redirect(url_for("index"))

    teacher_id = session.get("teacher_id")
    records = read_attendance_by_teacher(teacher_id)

    return render_template(
        "dashboard.html",
        records=records,
        teacher=session.get("username")
    )

# ================= ADMIN DASHBOARD =================
@app.route("/admin")
def admin_dashboard():
    if session.get("role") != "Admin":
        return redirect(url_for("index"))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT teacher_id, username FROM teachers")
    teachers = cur.fetchall()

    selected_teacher = request.args.get("teacher_id")
    records = []

    if selected_teacher:
        records = read_attendance_by_teacher(selected_teacher)

    conn.close()

    return render_template(
        "admin_dashboard.html",
        teachers=teachers,
        selected_teacher=selected_teacher,
        records=records
    )

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ================= RUN =================
def run_app():
    print("Starting Flask backend...")
    app.run(
        debug=False,
        port=5000,
        use_reloader=False
    )
