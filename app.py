from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='Fresh')
    priority = db.Column(db.String(20), default='Low')
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.id}>'

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task_content = request.form.get('content')
        task_priority = request.form.get('priority')

        if task_content:
            # Check if a task with the same content already exists
            existing_task = Task.query.filter_by(content=task_content).first()
            if existing_task:
                # Do not add duplicate task
                return redirect(url_for('index'))
            
            new_task = Task(content=task_content, priority=task_priority)
            try:
                db.session.add(new_task)
                db.session.commit()
                return redirect(url_for('index'))
            except Exception as e:
                return f"An error occurred while adding the task: {e}"
        else:
            return "Task content cannot be empty."
    
    tasks = Task.query.order_by(Task.date_created).all()
    fresh_tasks = [t for t in tasks if t.status == 'Fresh']
    ongoing_tasks = [t for t in tasks if t.status == 'Ongoing']
    completed_tasks = [t for t in tasks if t.status == 'Completed']
    
    return render_template('index.html', 
                           fresh_tasks=fresh_tasks,
                           ongoing_tasks=ongoing_tasks,
                           completed_tasks=completed_tasks)

@app.route('/update/<int:id>/<string:new_status>')
def update(id, new_status):
    task = Task.query.get_or_404(id)
    task.status = new_status
    try:
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        return f"An error occurred while updating the task: {e}"

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Task.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        return f"An error occurred while deleting the task: {e}"

@app.route('/reset')
def reset():
    try:
        db.session.query(Task).delete()
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        return f"An error occurred while resetting the tasks: {e}"

if __name__ == '__main__':
    app.run(debug=True)
