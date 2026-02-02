import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

DB_PATH = os.path.join(PROJECT_ROOT, "database", "database.db")


import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading
import sqlite3

from web_dashboard.app import run_app


# ================== BACKEND ==================
def start_backend():
    print("Starting Flask backend in background...")
    threading.Thread(target=run_app, daemon=True).start()


# ================== CONFIG ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "database", "database.db")

ENTRY_WIDTH = 28
FONT_LABEL = ("Arial", 12)
FONT_ENTRY = ("Arial", 13)
FONT_BUTTON = ("Arial", 12, "bold")


# ================== DATABASE HELPERS ==================
def get_db_connection():
    return sqlite3.connect(DB_PATH)


def validate_teacher(username, password):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT teacher_id FROM teachers WHERE username=? AND password=?",
        (username, password)
    )
    row = cur.fetchone()
    conn.close()

    return row[0] if row else None


def get_student_grade(student_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT grade_level FROM students WHERE student_id=?",
        (student_id,)
    )
    row = cur.fetchone()
    conn.close()

    return row[0] if row else None


def insert_attendance(data):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO attendance_logs
        (student_id, teacher_id, class_date, class_time,
         class_period, class_subject, grade_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()


# ================== FUNCTIONS ==================
def insert_attendance(data):
    print("INSERT DATA:", data)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO attendance_log
        (student_id, teacher_id, class_date, class_time,
         class_period, class_subject, grade_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()

    print("DB COMMIT SUCCESS")

#======SAVE ATTENDANCE======


def save_attendance():
    teacher_username = teacher_var.get()
    password = entry_password.get().strip()
    subject = entry_subject.get().strip()
    period = entry_period.get().strip()
    student_id = entry_id.get().strip()

    if not all([teacher_username, password, subject, period, student_id]):
        status_label.config(text="All fields are required.", fg="red")
        return

    if not student_id.isdigit():
        status_label.config(text="Student ID must be numeric.", fg="red")
        entry_id.delete(0, tk.END)
        return

    teacher_id = validate_teacher(teacher_username, password)
    if not teacher_id:
        status_label.config(text="Invalid teacher login.", fg="red")
        return

    grade_level = get_student_grade(student_id)
    if not grade_level:
        status_label.config(text="Student not found.", fg="red")
        return

    now = datetime.now()

    insert_attendance((
        student_id,
        teacher_id,
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S"),
        period,
        subject,
        grade_level
    ))

    entry_id.delete(0, tk.END)
    entry_id.focus()

    status_label.config(text="Attendance saved successfully.", fg="green")



# ================== UI ==================
window = tk.Tk()
window.title("Attendance System")
window.geometry("550x400")
window.resizable(False, False)

title = tk.Label(
    window,
    text="Sunflower Trilingual School",
    font=("Arial", 16, "bold")
)
title.pack(pady=15)

form = tk.Frame(window)
form.pack()


def form_row(row, label_text, widget):
    tk.Label(
        form,
        text=label_text,
        width=16,
        anchor="w",
        font=FONT_LABEL
    ).grid(row=row, column=0, padx=10, pady=8, sticky="w")

    widget.grid(row=row, column=1, padx=10, pady=8)


teacher_var = tk.StringVar()
teacher_dropdown = ttk.Combobox(
    form,
    textvariable=teacher_var,
    state="readonly",
    width=ENTRY_WIDTH,
    font=FONT_ENTRY
)
form_row(0, "Username", teacher_dropdown)

entry_password = tk.Entry(form, show="*", width=ENTRY_WIDTH, font=FONT_ENTRY)
form_row(1, "Password", entry_password)

entry_subject = tk.Entry(form, width=ENTRY_WIDTH, font=FONT_ENTRY)
form_row(2, "Subject", entry_subject)

entry_period = tk.Entry(form, width=ENTRY_WIDTH, font=FONT_ENTRY)
form_row(3, "Period", entry_period)

entry_id = tk.Entry(form, width=ENTRY_WIDTH, font=FONT_ENTRY)
form_row(4, "Scan Student ID", entry_id)
entry_id.focus()

save_btn = tk.Button(
    window,
    text="Save Attendance",
    width=22,
    bg="#2ecc71",
    fg="black",
    font=FONT_BUTTON,
    command=save_attendance
)
save_btn.pack(pady=18)

status_label = tk.Label(
    window,
    text="Waiting for scan...",
    fg="white",
    font=("Arial", 11)
)
status_label.pack(pady=6)


# ================== ENTRY POINT ==================
def main():
    start_backend()
    load_teachers()
    window.mainloop()


def load_teachers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT username FROM teachers")
    teacher_dropdown["values"] = [row[0] for row in cur.fetchall()]
    conn.close()


if __name__ == "__main__":
    main()
