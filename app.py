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

# -------------------- HTML + CSS + ANIMATION --------------------
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Student System</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(rgba(80,0,120,0.6), rgba(150,0,200,0.6)),
                        url('https://images.unsplash.com/photo-1567306226416-28f0efdc88ce');
            background-size: cover;
            background-position: center;
            text-align: center;
            margin: 0;
            padding: 0;
            animation: fadeIn 1.5s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .container {
            width: 70%;
            margin: 40px auto;
            background: rgba(255,255,255,0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            animation: slideUp 1s ease;
        }

        @keyframes slideUp {
            from { transform: translateY(50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        h1 {
            color: #6a0dad;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        input {
            padding: 10px;
            margin: 5px;
            border-radius: 5px;
            border: 1px solid #ccc;
            outline: none;
            transition: 0.3s;
        }

        input:focus {
            border-color: #a855f7;
            box-shadow: 0 0 8px #c77dff;
        }

        button {
            padding: 8px 12px;
            margin: 2px;
            border: none;
            color: white;
            cursor: pointer;
            border-radius: 5px;
            transition: 0.3s;
        }

        .add-btn { background: #8a2be2; }
        .add-btn:hover { transform: scale(1.1); background: #6a0dad; }

        .delete-btn { background: #ff4d6d; }
        .delete-btn:hover { transform: scale(1.1); background: #d90429; }

        .edit-btn { background: #c77dff; }
        .edit-btn:hover { transform: scale(1.1); background: #9d4edd; }

        table {
            width: 100%;
            margin-top: 20px;
            border-collapse: collapse;
            border-radius: 10px;
            overflow: hidden;
            animation: fadeIn 2s ease;
        }

        th, td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }

        th {
            background: #8a2be2;
            color: white;
        }

        tr {
            transition: 0.3s;
        }

        tr:hover {
            background: #f3e8ff;
            transform: scale(1.01);
        }
    </style>
</head>

<body>

<div class="container">
    <h1>🍇 Student Record of Section Grapes</h1>

    <input type="text" id="name" placeholder="Name">
    <input type="number" id="grade" placeholder="Grade">
    <input type="text" id="section" placeholder="Section">
    <button class="add-btn" onclick="addStudent()">Add</button>

    <table>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Grade</th>
            <th>Section</th>
            <th>Actions</th>
        </tr>

        {% for student in students %}
        <tr>
            <td>{{ student.id }}</td>
            <td>{{ student.name }}</td>
            <td>{{ student.grade }}</td>
            <td>{{ student.section }}</td>
            <td>
                <button class="edit-btn"
                    onclick="editStudent({{ student.id }}, '{{ student.name }}', {{ student.grade }}, '{{ student.section }}')">
                    Edit
                </button>

                <button class="delete-btn"
                    onclick="deleteStudent({{ student.id }})">
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
    }).then(() => location.reload());
}

function deleteStudent(id) {
    fetch('/api/students/' + id, {
        method: 'DELETE'
    }).then(() => location.reload());
}

function editStudent(id, name, grade, section) {
    const newName = prompt("Enter name:", name);
    const newGrade = prompt("Enter grade:", grade);
    const newSection = prompt("Enter section:", section);

    if (!newName || !newGrade || !newSection) return;

    fetch('/api/students/' + id, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: newName,
            grade: newGrade,
            section: newSection
        })
    }).then(() => location.reload());
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

# -------------------- GET --------------------
@app.route('/api/students', methods=['GET'])
def get_students():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()

    return jsonify([dict(s) for s in students])

# -------------------- ADD --------------------
@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json()

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

    return jsonify({"message": "Added"})

# -------------------- UPDATE --------------------
@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE students
        SET name=?, grade=?, section=?
        WHERE id=?
    """, (data["name"], data["grade"], data["section"], id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Updated"})

# -------------------- DELETE --------------------
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
