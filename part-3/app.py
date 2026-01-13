"""
Part 3: Flask-SQLAlchemy ORM
============================
Say goodbye to raw SQL! Use Python classes to work with databases.

What You'll Learn:
- Setting up Flask-SQLAlchemy
- Creating Models (Python classes = database tables)
- ORM queries instead of raw SQL
- Relationships between tables (One-to-Many)

Prerequisites: Complete part-1 and part-2
Install: pip install flask-sqlalchemy
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy  # Import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'  # Database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable warning

db = SQLAlchemy(app)  # Initialize SQLAlchemy with app


# =============================================================================
# MODELS (Python Classes = Database Tables)
# =============================================================================

class Course(db.Model):  # Course table
    id = db.Column(db.Integer, primary_key=True)  # Auto-increment ID
    name = db.Column(db.String(100), nullable=False)  # Course name
    description = db.Column(db.Text)  # Optional description

    # Relationship: One Course has Many Students
    students = db.relationship('Student', backref='course', lazy=True)
    teachers = db.relationship('Teacher', backref='course', lazy=True)

    def __repr__(self):  # How to display this object
        return f'<Course {self.name}>'


class Student(db.Model):  # Student table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # unique=True means no duplicates

    # Foreign Key: Links student to a course
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'


class Teacher(db.Model):  # Student table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  # unique=True means no duplicates

    # Foreign Key: Links student to a course
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __repr__(self):
        return f'<Teacher {self.name}>'
# =============================================================================
# ROUTES - Using ORM instead of raw SQL
# =============================================================================

@app.route('/')
def index():
    # OLD WAY (raw SQL): conn.execute('SELECT * FROM students').fetchall()
    # NEW WAY (ORM):
    students = Student.query.order_by(Student.id.desc()).limit(4).all()  # Get all students
    return render_template('index.html', students=students)

@app.route('/teachers')
def teachers():
    teachers = Teacher.query.all()  
    return render_template('teachers.html', teachers=teachers)

@app.route('/courses')
def courses():
    all_courses = Course.query.order_by(Course.name.asc()).all()  # Get all courses
    return render_template('courses.html', courses=all_courses)


@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course_id = request.form['course_id']

        # OLD WAY: conn.execute('INSERT INTO students...')
        # NEW WAY:
        new_student = Student(name=name, email=email, course_id=course_id)  # Create object
        db.session.add(new_student)  # Add to session
        db.session.commit()  # Save to database

        flash('Student added successfully!', 'success')
        return redirect(url_for('index'))

    courses = Course.query.all()  # Get courses for dropdown
    return render_template('add.html', courses=courses)


@app.route('/addteacher', methods=['GET', 'POST'])
def add_teacher():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course_id = request.form['course_id']

        # OLD WAY: conn.execute('INSERT INTO students...')
        # NEW WAY:
        new_teacher = Teacher(name=name, email=email, course_id=course_id)  # Create object
        db.session.add(new_teacher)  # Add to session
        db.session.commit()  # Save to database

        flash('Teacher added successfully!', 'success')
        return redirect(url_for('index'))

    courses = Course.query.all()  # Get courses for dropdown
    return render_template('addteacher.html', courses=courses)



@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    # OLD WAY: conn.execute('SELECT * FROM students WHERE id = ?', (id,))
    # NEW WAY:
    student = Student.query.get_or_404(id)  # Get by ID or show 404 error

    if request.method == 'POST':
        student.name = request.form['name']  # Just update the object
        student.email = request.form['email']
        student.course_id = request.form['course_id']

        db.session.commit()  # Save changes
        flash('Student updated!', 'success')
        return redirect(url_for('index'))

    courses = Course.query.all()
    return render_template('edit.html', student=student, courses=courses)


@app.route('/editteacher/<int:id>', methods=['GET', 'POST'])
def edit_teacher(id):
    # OLD WAY: conn.execute('SELECT * FROM students WHERE id = ?', (id,))
    # NEW WAY:
    teacher = Teacher.query.get_or_404(id)  # Get by ID or show 404 error

    if request.method == 'POST':
        teacher.name = request.form['name']  # Just update the object
        teacher.email = request.form['email']
        teacher.course_id = request.form['course_id']

        db.session.commit()  # Save changes
        flash('Teacher updated!', 'success')
        return redirect(url_for('index'))

    courses = Course.query.all()
    return render_template('editteacher.html', teacher=teacher, courses=courses)


@app.route('/search-teachers')
def search_teachers():
    # Get the 'q' parameter from the URL (e.g., /search-teachers?q=John)
    query = request.args.get('q', '')
    
    if query:
        # Use filter with LIKE for a "contains" search
        # %query% means the text can be anywhere in the name
        results = Teacher.query.filter(Teacher.name.like(f"%{query}%")).all()
    else:
        results = Teacher.query.all()
        
    return render_template('teachers.html', teachers=results, search_text=query)


@app.route('/delete/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)  # Delete the object
    db.session.commit()

    flash('Student deleted!', 'danger')
    return redirect(url_for('index'))


@app.route('/delete/<int:id>')
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)  # Delete the object
    db.session.commit()

    flash('Teacher deleted!', 'danger')
    return redirect(url_for('index'))


@app.route('/add-course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '') 

        # Create the course and link the teacher_id
        # We convert teacher_id to int, or None if no teacher was selected
        new_course = Course(
            name=name, 
            description=description
        )
        
        db.session.add(new_course)
        db.session.commit()

        flash('Course added successfully with assigned teacher!', 'success')
        return redirect(url_for('courses'))

    # Fetch all teachers so the dropdown has options
    teachers = Teacher.query.all()
    return render_template('add_course.html', teachers=teachers)


# =============================================================================
# CREATE TABLES AND ADD SAMPLE DATA
# =============================================================================

def init_db():
    """Create tables and add sample courses if empty"""
    with app.app_context():
        db.create_all()  # Create all tables based on models

        # Add sample courses if none exist
        if Course.query.count() == 0:
            sample_courses = [
                Course(name='Python Basics', description='Learn Python programming fundamentals'),
                Course(name='Web Development', description='HTML, CSS, JavaScript and Flask'),
                Course(name='Data Science', description='Data analysis with Python'),
            ]
            db.session.add_all(sample_courses)  # Add multiple at once
            db.session.commit()
            print('Sample courses added!')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)


# =============================================================================
# ORM vs RAW SQL COMPARISON:
# =============================================================================
#
# Operation      | Raw SQL                          | SQLAlchemy ORM
# ---------------|----------------------------------|---------------------------
# Get all        | SELECT * FROM students           | Student.query.all()
# Get by ID      | SELECT * WHERE id = ?            | Student.query.get(id)
# Filter         | SELECT * WHERE name = ?          | Student.query.filter_by(name='John')
# Insert         | INSERT INTO students VALUES...   | db.session.add(student)
# Update         | UPDATE students SET...           | student.name = 'New'; db.session.commit()
# Delete         | DELETE FROM students WHERE...    | db.session.delete(student)
#
# =============================================================================
# COMMON QUERY METHODS:
# =============================================================================
#
# Student.query.all()                    - Get all records
# Student.query.first()                  - Get first record
# Student.query.get(1)                   - Get by primary key
# Student.query.get_or_404(1)            - Get or show 404 error
# Student.query.filter_by(name='John')   - Filter by exact value
# Student.query.filter(Student.name.like('%john%'))  - Filter with LIKE
# Student.query.order_by(Student.name)   - Order results
# Student.query.count()                  - Count records
#
# =============================================================================


# =============================================================================
# EXERCISE:
# =============================================================================
#
# 1. Add a `Teacher` model with a relationship to Course
# 2. Try different query methods: `filter()`, `order_by()`, `limit()`
#
# =============================================================================
