from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# -------------------- IN-MEMORY DATABASE --------------------
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
    return "Student Attendance API"

# -------------------- ADD STUDENT --------------------
@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()

    if not data or not all(k in data for k in ("name", "grade", "section")):
        return jsonify({"error": "Missing required fields"}), 400

    new_student = {
        "id": students[-1]["id"] + 1 if students else 1,
        "name": data["name"],
        "grade": data["grade"],
        "section": data["section"],
        "attendance": []  # empty attendance list
    }

    students.append(new_student)

    return jsonify({
        "message": "Student added successfully",
        "student": new_student
    }), 201

# -------------------- GET ALL STUDENTS --------------------
@app.route('/students', methods=['GET'])
def get_students():
    return jsonify(students)

# -------------------- MARK ATTENDANCE --------------------
@app.route('/students/<int:id>/attendance', methods=['POST'])
def mark_attendance(id):
    student = next((s for s in students if s["id"] == id), None)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json()

    if "status" not in data:
        return jsonify({"error": "Status required (Present/Absent)"}), 400

    record = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "status": data["status"]
    }

    student["attendance"].append(record)

    return jsonify({
        "message": "Attendance marked",
        "attendance": record
    })

# -------------------- VIEW ATTENDANCE --------------------
@app.route('/students/<int:id>/attendance', methods=['GET'])
def get_attendance(id):
    student = next((s for s in students if s["id"] == id), None)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({
        "name": student["name"],
        "attendance": student["attendance"]
    })

# -------------------- UPDATE STUDENT --------------------
@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    student = next((s for s in students if s["id"] == id), None)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json()

    student["name"] = data.get("name", student["name"])
    student["grade"] = data.get("grade", student["grade"])
    student["section"] = data.get("section", student["section"])

    return jsonify({
        "message": "Student updated",
        "student": student
    })

# -------------------- DELETE STUDENT --------------------
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    global students

    student = next((s for s in students if s["id"] == id), None)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    students = [s for s in students if s["id"] != id]

    return jsonify({"message": "Student deleted"})

# -------------------- RUN --------------------
if __name__ == '__main__':
    app.run(debug=True)
