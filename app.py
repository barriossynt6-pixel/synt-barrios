from flask import Flask, jsonify, request

app = Flask(__name__)

# -------------------- IN-MEMORY DATABASE --------------------
students = [
    {"id": 1, "name": "John Doe", "grade": 10, "section": "Zechariah"},
    {"id": 2, "name": "Jane Smith", "grade": 9, "section": "Genesis"}
]

# -------------------- HOME --------------------
@app.route('/')
def home():
    return "Welcome to my Flask API with CRUD!"

# -------------------- CREATE --------------------
@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()

    # Validate input
    if not data or not all(k in data for k in ("name", "grade", "section")):
        return jsonify({"error": "Missing required fields"}), 400

    new_student = {
        "id": students[-1]["id"] + 1 if students else 1,
        "name": data["name"],
        "grade": data["grade"],
        "section": data["section"]
    }

    students.append(new_student)

    return jsonify({
        "message": "Student added successfully",
        "student": new_student
    }), 201

# -------------------- READ ALL --------------------
@app.route('/students', methods=['GET'])
def get_students():
    return jsonify({
        "count": len(students),
        "students": students
    })

# -------------------- READ ONE --------------------
@app.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    student = next((s for s in students if s["id"] == id), None)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(student)

# -------------------- UPDATE --------------------
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
        "message": "Student updated successfully",
        "student": student
    })

# -------------------- DELETE --------------------
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    global students

    student = next((s for s in students if s["id"] == id), None)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    students = [s for s in students if s["id"] != id]

    return jsonify({
        "message": "Student deleted successfully"
    })

# -------------------- RUN APP --------------------
if __name__ == '__main__':
    app.run(debug=True)
