import tkinter as tk
from tkinter import messagebox
import sqlite3
import os

# ================== DATABASE CONFIG ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

# ================== DATABASE HELPERS ==================
def get_db_connection():
    return sqlite3.connect(DB_PATH)


def student_exists(student_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT 1 FROM students WHERE student_id=?",
        (student_id,)
    )

    exists = cur.fetchone() is not None
    conn.close()
    return exists


def insert_student(student_id, full_name, grade_level):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO students (student_id, full_name, grade_level)
        VALUES (?, ?, ?)
    """, (student_id, full_name, grade_level))

    conn.commit()
    conn.close()


# ================== SAVE STUDENT ==================
def save_student():
    student_id = entry_id.get().strip()
    full_name = entry_name.get().strip()
    grade_level = entry_grade.get().strip()

    if not all([student_id, full_name, grade_level]):
        messagebox.showerror("Error", "All fields are required.")
        return

    if not student_id.isdigit():
        messagebox.showerror("Error", "Student ID must be numeric.")
        return

    if student_exists(student_id):
        messagebox.showerror("Error", "Student already exists.")
        return

    insert_student(student_id, full_name, grade_level)

    messagebox.showinfo("Success", "Student registered successfully!")

    entry_id.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_grade.delete(0, tk.END)
    entry_id.focus()


# ================== UI ==================
window = tk.Tk()
window.title("New Student Registration")
window.geometry("420x300")
window.resizable(False, False)

title = tk.Label(
    window,
    text="Student Registration",
    font=("Arial", 16, "bold")
)
title.pack(pady=15)

form = tk.Frame(window)
form.pack(pady=10)


def form_row(row, label, widget):
    tk.Label(
        form,
        text=label,
        width=14,
        anchor="w",
        font=("Arial", 12)
    ).grid(row=row, column=0, padx=10, pady=8)

    widget.grid(row=row, column=1, padx=10, pady=8)


entry_id = tk.Entry(form, width=25, font=("Arial", 12))
form_row(0, "Student ID", entry_id)

entry_name = tk.Entry(form, width=25, font=("Arial", 12))
form_row(1, "Full Name", entry_name)

entry_grade = tk.Entry(form, width=25, font=("Arial", 12))
form_row(2, "Grade Level", entry_grade)

save_btn = tk.Button(
    window,
    text="Save Student",
    font=("Arial", 12, "bold"),
    width=20,
    bg="#2ecc71",
    fg="black",
    command=save_student
)
save_btn.pack(pady=20)

entry_id.focus()

# ================== RUN ==================
window.mainloop()