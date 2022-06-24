import os
from datetime import datetime

from flask import Flask, request
from flask.templating import render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
db_name = "databases/todo.db"
history_name = "databases/history.db"

app.debug = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_BINDS"] = {
    'todo': f"sqlite:///{db_name}",
    'history': f"sqlite:///{history_name}"
}

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Todo(db.Model):
    """
    Model for the TODO object with 3 attributes : category of the task, task description and date.
    """
    __bind_key__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(60), unique=False, nullable=True)
    task = db.Column(db.String(250), unique=False, nullable=True)
    created = db.Column(db.String(100), unique=False, nullable=True)

    def __repr__(self):
        return '<Task %r>' % self.task


class History(db.Model):
    """
    Model for the History object with 4 attributes :
    category of the task, task description, date of creation and date of deletion.
    """
    __bind_key__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(60), unique=False, nullable=True)
    task = db.Column(db.String(250), unique=False, nullable=True)
    created = db.Column(db.String(100), unique=False, nullable=True)
    ended = db.Column(db.String(100), unique=False, nullable=True)

    def __repr__(self):
        return '<Task %r>' % self.task


@app.route("/", methods=["GET"])
def home():
    """Show all current tasks to do"""
    all_tasks = Todo.query.all()
    return render_template('index.html', all_tasks=all_tasks)


@app.route("/add_data", methods=["POST"])
def add_new_data():
    """Add data to the TODO database"""
    _category = request.form.get("category")
    _task = request.form.get("task")
    _now = datetime.now().strftime('%d %b %Y, at %H:%M:%S')
    _todo = Todo(category=_category, task=_task, created=_now)
    db.session.add(_todo)
    db.session.commit()
    return home()


@app.route('/delete/<int:id>', methods=["POST"])
def remove(id):
    """Remove data from TODO database and so add it to history"""
    todo = Todo.query.get(id)
    _now = datetime.now().strftime('%d %b %Y, at %H:%M:%S')
    _history = History(category=todo.category, task=todo.task,
                       created=todo.created, ended=_now)
    db.session.add(_history)
    db.session.delete(todo)
    db.session.commit()
    return home()


@app.route('/history')
def show_history():
    """Show all tasks already done"""
    history_tasks = History.query.all()
    return render_template('history.html', history_tasks=history_tasks)


if __name__ == "__main__":
    if os.listdir("./databases") == ['.gitkeep']:
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
