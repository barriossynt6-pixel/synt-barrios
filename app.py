from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# -------------------- DATABASE --------------------
students = [
    {
        "id": 1,
        "name": "John Doe",
        "grade": 10,
        "section": "Zechariah",
        "attendance": []
    }
]

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

    new_student = {
        "id": students[-1]["id"] + 1 if students else 1,
        "name": data["name"],
        "grade": data["grade"],
        "section": data["section"],
        "attendance": []
    }

    students.append(new_student)

    return jsonify({"message": "Student added", "student": new_student}), 201

# -------------------- MARK ATTENDANCE --------------------
@app.route('/students/<int:id>/attendance', methods=['POST'])
def mark_attendance(id):
    student = next((s for s in students if s["id"] == id), None)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json()

    if "status" not in data:
        return jsonify({"error": "Status required"}), 400

    record = {
        "date": data.get("date", datetime.now().strftime("%Y-%m-%d")),
        "status": data["status"]
    }

    student["attendance"].append(record)

    return jsonify({"message": "Attendance recorded", "record": record})

# -------------------- FULL ATTENDANCE RECORD --------------------
@app.route('/students/<int:id>/record', methods=['GET'])
def attendance_record(id):
    student = next((s for s in students if s["id"] == id), None)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    attendance = student["attendance"]

    present_count = sum(1 for a in attendance if a["status"] == "Present")
    absent_count = sum(1 for a in attendance if a["status"] == "Absent")

    return jsonify({
        "student": student["name"],
        "total_days": len(attendance),
        "present": present_count,
        "absent": absent_count,
        "attendance": attendance
    })

# -------------------- FILTER BY DATE --------------------
@app.route('/students/<int:id>/record/<date>', methods=['GET'])
def attendance_by_date(id, date):
    student = next((s for s in students if s["id"] == id), None)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    filtered = [a for a in student["attendance"] if a["date"] == date]

    return jsonify({
        "student": student["name"],
        "date": date,
        "records": filtered
    })

# -------------------- GET ALL STUDENTS --------------------
@app.route('/students', methods=['GET'])
def get_students():
    return jsonify(students)

# -------------------- DELETE STUDENT --------------------
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    global students

    student = next((s for s in students if s["id"] == id), None)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    students = [s for s in students if s["id"] != id]

    return jsonify({"message": "Deleted successfully"})

# -------------------- RUN --------------------
if __name__ == '__main__':
    app.run(debug=True)
