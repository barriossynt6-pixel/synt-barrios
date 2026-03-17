from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory "database"
students = [
    {"id": 1, "name": "John Doe", "grade": 10, "section": "Zechariah"},
    {"id": 2, "name": "Jane Smith", "grade": 9, "section": "Genesis"}
]

# Home route
@app.route('/')
def home():
    return "Welcome to my Flask API with CRUD!"

# CREATE - Add a new student
@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    
    new_student = {
        "id": students[-1]["id"] + 1 if students else 1,
        "name": data["name"],
        "grade": data["grade"],
        "section": data["section"]
    }
    
    students.append(new_student)
    return jsonify(new_student), 201

# READ - Get all students
@app.route('/students', methods=['GET'])
def get_students():
    return jsonify(students)

# READ - Get single student by ID
@app.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    student = next((s for s in students if s["id"] == id), None)
    
    if student:
        return jsonify(student)
    return jsonify({"error": "Student not found"}), 404

# UPDATE - Update student by ID
@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    student = next((s for s in students if s["id"] == id), None)
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    data = request.get_json()
    
    student["name"] = data.get("name", student["name"])
    student["grade"] = data.get("grade", student["grade"])
    student["section"] = data.get("section", student["section"])
    
    return jsonify(student)

# DELETE - Delete student by ID
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    global students
    students = [s for s in students if s["id"] != id]
    
    return jsonify({"message": "Student deleted successfully"})

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
