from flask import Flask, jsonify, request, render_template_string
import sqlite3

app = Flask(__name__)
DB_NAME = "students.db"

# -------------------- DATABASE --------------------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

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

    conn.commit()
    conn.close()

init_db()

# -------------------- HTML + CSS --------------------
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Student System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            text-align: center;
        }

        h1 {
            color: #333;
        }

        .container {
            width: 60%;
            margin: auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }

        input {
            padding: 10px;
            margin: 5px;
            width: 25%;
        }

        button {
            padding: 10px 15px;
            background: #007BFF;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 5px;
        }

        button:hover {
            background: #0056b3;
        }

        .delete-btn {
            background: red;
        }

        .delete-btn:hover {
            background: darkred;
        }

        table {
            width: 100%;
            margin-top: 20px;
            border-collapse: collapse;
        }

        th, td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }

        th {
            background: #007BFF;
            color: white;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>Student Management System</h1>

    <input type="text" id="name" placeholder="Name">
    <input type="number" id="grade" placeholder="Grade">
    <input type="text" id="section" placeholder="Section">
    <br>
    <button onclick="addStudent()">Add Student</button>

    <table>
        <tr>
            <th>Name</th>
            <th>Grade</th>
            <th>Section</th>
            <th>Action</th>
        </tr>

        {% for student in students %}
        <tr>
            <td>{{ student.name }}</td>
            <td>{{ student.grade }}</td>
            <td>{{ student.section }}</td>
            <td>
                <button class="delete-btn" onclick="deleteStudent({{ student.id }})">
                    Delete
                </button>
            </td>
        </tr>
        {% endfor %}
    </table>
</div>

<script>
function addStudent() {
    const name = document.getElementById('name').value;
    const grade = document.getElementById('grade').value;
    const section = document.getElementById('section').value;

    fetch('/api/students', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, grade, section })
    })
    .then(res => res.json())
    .then(() => location.reload());
}

function deleteStudent(id) {
    fetch('/api/students/' + id, {
        method: 'DELETE'
    })
    .then(() => location.reload());
}
</script>

</body>
</html>
"""

# -------------------- HOME --------------------
@app.route('/')
def home():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()

    return render_template_string(HTML_PAGE, students=students)

# -------------------- API --------------------
@app.route('/api/students', methods=['GET'])
def get_students():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()

    return jsonify([dict(s) for s in students])

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid input"}), 400

    name = data.get("name")
    grade = data.get("grade")
    section = data.get("section")

    if not all([name, grade, section]):
        return jsonify({"error": "All fields required"}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students (name, grade, section) VALUES (?, ?, ?)",
        (name, grade, section)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Student added"})

@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Deleted"})

# -------------------- RUN --------------------
if __name__ == '__main__':
    app.run(debug=True)
