from flask import Flask, jsonify, request
from datetime import datetime
import sqlite3

app = Flask(__name__)
DB_NAME = "students.db"

# -------------------- DATABASE HELPER --------------------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------- DATABASE SETUP --------------------
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            grade INTEGER NOT NULL,
            section TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date TEXT,
            status TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# -------------------- HOME --------------------
@app.route('/')
def home():
    return jsonify({"message": "Student Attendance Record API"})

# -------------------- ADD STUDENT --------------------
@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    name = data.get("name")
    grade = data.get("grade")
    section = data.get("section")

    if not all([name, grade, section]):
        return jsonify({"error": "Missing fields"}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students (name, grade, section) VALUES (?, ?, ?)",
        (name, grade, section)
    )
    conn.commit()

    student_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "message": "Student added",
        "student": {
            "id": student_id,
            "name": name,
            "grade": grade,
            "section": section
        }
    }), 201

# -------------------- UPDATE STUDENT --------------------
@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id = ?", (id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    name = data.get("name")
    grade = data.get("grade")
    section = data.get("section")

    cursor.execute("""
        UPDATE students
        SET name = COALESCE(?, name),
            grade = COALESCE(?, grade),
            section = COALESCE(?, section)
        WHERE id = ?
    """, (name, grade, section, id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Student updated"})

# -------------------- MARK ATTENDANCE --------------------
@app.route('/students/<int:id>/attendance', methods=['POST'])
def mark_attendance(id):
    data = request.get_json()

    if not data or "status" not in data:
        return jsonify({"error": "Status required"}), 400

    status = data["status"].capitalize()
    if status not in ["Present", "Absent"]:
        return jsonify({"error": "Status must be Present or Absent"}), 400

    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id = ?", (id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    cursor.execute(
        "INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
        (id, date, status)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Attendance recorded",
        "record": {"date": date, "status": status}
    })

# -------------------- DELETE ATTENDANCE --------------------
@app.route('/attendance/<int:attendance_id>', methods=['DELETE'])
def delete_attendance(attendance_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM attendance WHERE id = ?", (attendance_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Attendance deleted"})

# -------------------- FULL RECORD --------------------
@app.route('/students/<int:id>/record', methods=['GET'])
def attendance_record(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM students WHERE id = ?", (id,))
    student = cursor.fetchone()

    if not student:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    cursor.execute("""
        SELECT id, date, status 
        FROM attendance 
        WHERE student_id = ?
        ORDER BY date DESC
    """, (id,))
    records = cursor.fetchall()

    conn.close()

    attendance = [
        {"id": r["id"], "date": r["date"], "status": r["status"]}
        for r in records
    ]

    present = sum(1 for r in attendance if r["status"] == "Present")
    absent = sum(1 for r in attendance if r["status"] == "Absent")

    return jsonify({
        "student": student["name"],
        "total_days": len(attendance),
        "present": present,
        "absent": absent,
        "attendance": attendance
    })

# -------------------- FILTER BY DATE --------------------
@app.route('/students/<int:id>/record/<date>', methods=['GET'])
def attendance_by_date(id, date):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, date, status 
        FROM attendance 
        WHERE student_id = ? AND date = ?
    """, (id, date))

    records = cursor.fetchall()
    conn.close()

    return jsonify({
        "student_id": id,
        "date": date,
        "records": [
            {"id": r["id"], "date": r["date"], "status": r["status"]}
            for r in records
        ]
    })

# -------------------- GET ALL STUDENTS --------------------
@app.route('/students', methods=['GET'])
def get_students():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    conn.close()

    return jsonify([
        {
            "id": r["id"],
            "name": r["name"],
            "grade": r["grade"],
            "section": r["section"]
        }
        for r in rows
    ])

# -------------------- DELETE STUDENT --------------------
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id = ?", (id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    cursor.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Student deleted successfully"})

# -------------------- RUN --------------------
if __name__ == '__main__':
    app.run(debug=True)
