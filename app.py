from flask import Flask, jsonify, request
from datetime import datetime
import sqlite3

app = Flask(__name__)
DB_NAME = "students.db"

# -------------------- DATABASE SETUP --------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            grade INTEGER,
            section TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date TEXT,
            status TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# -------------------- HOME --------------------
@app.route('/')
def home():
    return "Student Attendance Record API"

# -------------------- ADD STUDENT --------------------
@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()

    if not data or not all(k in data for k in ("name", "grade", "section")):
        return jsonify({"error": "Missing fields"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students (name, grade, section) VALUES (?, ?, ?)",
        (data["name"], data["grade"], data["section"])
    )

    conn.commit()
    student_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "message": "Student added",
        "student": {
            "id": student_id,
            "name": data["name"],
            "grade": data["grade"],
            "section": data["section"]
        }
    }), 201

# -------------------- MARK ATTENDANCE --------------------
@app.route('/students/<int:id>/attendance', methods=['POST'])
def mark_attendance(id):
    data = request.get_json()

    if not data or "status" not in data:
        return jsonify({"error": "Status required"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id = ?", (id,))
    student = cursor.fetchone()

    if not student:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))

    cursor.execute(
        "INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
        (id, date, data["status"])
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Attendance recorded",
        "record": {
            "date": date,
            "status": data["status"]
        }
    })

# -------------------- FULL RECORD --------------------
@app.route('/students/<int:id>/record', methods=['GET'])
def attendance_record(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM students WHERE id = ?", (id,))
    student = cursor.fetchone()

    if not student:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    cursor.execute(
        "SELECT date, status FROM attendance WHERE student_id = ?", (id,)
    )
    records = cursor.fetchall()

    conn.close()

    attendance = [{"date": r[0], "status": r[1]} for r in records]

    present = sum(1 for r in attendance if r["status"] == "Present")
    absent = sum(1 for r in attendance if r["status"] == "Absent")

    return jsonify({
        "student": student[0],
        "total_days": len(attendance),
        "present": present,
        "absent": absent,
        "attendance": attendance
    })

# -------------------- FILTER BY DATE --------------------
@app.route('/students/<int:id>/record/<date>', methods=['GET'])
def attendance_by_date(id, date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT date, status FROM attendance WHERE student_id = ? AND date = ?",
        (id, date)
    )
    records = cursor.fetchall()

    conn.close()

    return jsonify({
        "student_id": id,
        "date": date,
        "records": [{"date": r[0], "status": r[1]} for r in records]
    })

# -------------------- GET ALL STUDENTS --------------------
@app.route('/students', methods=['GET'])
def get_students():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()

    conn.close()

    students = [
        {"id": r[0], "name": r[1], "grade": r[2], "section": r[3]}
        for r in rows
    ]

    return jsonify(students)

# -------------------- DELETE STUDENT --------------------
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()

    conn.close()

    return jsonify({"message": "Deleted successfully"})

# -------------------- RUN --------------------
if __name__ == '__main__':
    app.run(debug=True)
