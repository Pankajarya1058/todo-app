import os
import flask
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask application
app = Flask(__name__)

# --- 1. Database Configuration ---
# Uses environment variable for connection, e.g.:
# export DATABASE_URL="mysql+mysqlclient://user:password@localhost:3306/todo_db"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    # Fallback/default URL (replace with your actual credentials if not using env vars)
    'mysql+pymysql://user:password@localhost/mydb' 
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)

# --- 2. Database Model ---
# Defines the structure for a single To-Do item
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    is_complete = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Task {self.id}: {self.content}>'

# --- 3. HTML Template (Single Page) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Flask To-Do App</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f3f4f6; }
        .completed { text-decoration: line-through; color: #9ca3af; }
    </style>
</head>
<body class="min-h-screen p-8">

    <div class="max-w-xl mx-auto">
        <h1 class="text-4xl font-extrabold text-teal-700 mb-8 text-center">
            My To-Do List
        </h1>

        <!-- Add New Task Form -->
        <div class="bg-white p-6 rounded-xl shadow-lg mb-8 border border-teal-200">
            <h2 class="text-2xl font-semibold text-gray-700 mb-4">Add a New Task</h2>
            <form method="POST" action="{{ url_for('home') }}" class="flex space-x-3">
                <input 
                    type="text" 
                    name="content" 
                    placeholder="e.g., Finish Flask app integration..."
                    required
                    maxlength="200"
                    class="flex-grow p-3 border border-gray-300 rounded-lg focus:ring-teal-500 focus:border-teal-500 transition duration-150"
                >
                <button 
                    type="submit" 
                    class="bg-teal-600 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-teal-700 transition duration-150 transform hover:scale-105"
                >
                    Add Task
                </button>
            </form>
        </div>

        <!-- To-Do List -->
        <div class="space-y-3">
            {% for task in tasks %}
                <div class="flex items-center bg-white p-4 rounded-lg shadow-md border {% if task.is_complete %} border-green-300 {% else %} border-gray-200 {% endif %} transition duration-200">
                    
                    <!-- Task Content -->
                    <span class="flex-grow text-lg {% if task.is_complete %} completed {% else %} text-gray-800 {% endif %}">
                        {{ task.content }}
                    </span>
                    
                    <!-- Actions -->
                    <div class="flex space-x-2 ml-4">
                        <!-- Complete Button -->
                        {% if not task.is_complete %}
                            <a href="{{ url_for('complete', id=task.id) }}" class="p-2 text-white bg-green-500 rounded-full hover:bg-green-600 transition duration-150" title="Mark Complete">
                                <!-- Check Icon -->
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                            </a>
                        {% endif %}

                        <!-- Delete Button -->
                        <a href="{{ url_for('delete_task', id=task.id) }}" class="p-2 text-white bg-red-500 rounded-full hover:bg-red-600 transition duration-150" title="Delete Task">
                            <!-- Trash Icon -->
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                        </a>
                    </div>
                </div>
            {% else %}
                <div class="bg-blue-100 text-blue-800 p-4 rounded-lg text-center font-medium">
                    You're all caught up! Add a task above.
                </div>
            {% endfor %}
        </div>
        
        <div class="mt-10 text-center text-gray-500 text-sm">
            <p>Flask Version: {{ flask_version }}</p>
        </div>
    </div>

</body>
</html>
"""

# --- 4. Application Routes ---
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # CREATE: Add a new task
        content = request.form.get('content')
        if content:
            new_task = Todo(content=content)
            try:
                db.session.add(new_task)
                db.session.commit()
            except Exception as e:
                print(f"Database Error on CREATE: {e}")
                db.session.rollback() 
        return redirect(url_for('home'))

    # READ: Retrieve all tasks (ordered by incomplete first)
    tasks = Todo.query.order_by(Todo.is_complete.asc(), Todo.id.desc()).all()

    return render_template_string(
        HTML_TEMPLATE,
        tasks=tasks,
        flask_version=flask.__version__
    )

@app.route('/complete/<int:id>')
def complete(id):
    # UPDATE: Toggle the completion status of a task
    task = Todo.query.get_or_404(id)
    task.is_complete = True # Simple complete-only operation
    
    try:
        db.session.commit()
    except Exception as e:
        print(f"Database Error on UPDATE: {e}")
        db.session.rollback()
        
    return redirect(url_for('home'))

@app.route('/delete/<int:id>')
def delete_task(id):
    # DELETE: Remove a task permanently
    task = Todo.query.get_or_404(id)
    
    try:
        db.session.delete(task)
        db.session.commit()
    except Exception as e:
        print(f"Database Error on DELETE: {e}")
        db.session.rollback()
        
    return redirect(url_for('home'))


# The standard way to run a Flask app when executed directly
if __name__ == '__main__':
    # Add application context wrapper to automatically create tables
    with app.app_context():
        # This checks if the tables exist and creates them if they do not.
        db.create_all()
        print("Database tables checked and created if needed.")
        
    # host='0.0.0.0' makes it accessible inside Docker and across your network
    app.run(debug=True, host='0.0.0.0')
