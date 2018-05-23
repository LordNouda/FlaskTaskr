#################
# #  imports  # #
#################


from functools import wraps
from flask import Flask, flash, redirect, render_template, \
    request, session, url_for
from forms import AddTaskForm, RegisterForm, LoginForm
from flask_sqlalchemy import SQLAlchemy


################
# #  config  # #
################


app = Flask(__name__)
app.config.from_pyfile('_config.py')
db = SQLAlchemy(app)

# even with flake8 error E402 this import need to be below the "db = ..." line
from models import Task, User


#################
# #  helpers  # #
#################


def login_required(test):
    """Check if user has logged in."""
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


################
# #  routes  # #
################


@app.route('/logout/')
def logout():
    """Log out a user."""
    session.pop('logged_in', None)
    flash('Goodbye!')
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def login():
    """Log in a user."""
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(name=request.form['name']).first()
            if user is not None and user.password == request.form['password']:
                session['logged_in'] = True
                flash('Welcome!')
                return redirect(url_for('tasks'))
            else:
                error = 'Invalid Credentials. Please try again.'
        else:
            error = 'Both fields are required.'
    return render_template('login.html', form=form, error=error)


@app.route('/tasks/')
@login_required
def tasks():
    """Show the tasks page."""
    open_tasks = db.session.query(Task) \
        .filter_by(status='1') \
        .order_by(Task.due_date.asc())
    closed_tasks = db.session.query(Task) \
        .filter_by(status='0') \
        .order_by(Task.due_date.asc())
    return render_template(
        'tasks.html',
        form=AddTaskForm(request.form),
        open_tasks=open_tasks,
        closed_tasks=closed_tasks
    )


@app.route('/add/', methods=['POST'])
@login_required
def new_task():
    """Insert new task into the database."""
    form = AddTaskForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_task = Task(
                form.name.data,
                form.due_date.data,
                form.priority.data,
                '1'
            )
            db.session.add(new_task)
            db.session.commit()
            flash('New entry was successfully posted. Thanks.')
    return redirect(url_for('tasks'))


@app.route('/complete/<int:task_id>/')
@login_required
def complete(task_id):
    """Mark given task as complete."""
    new_id = task_id
    db.session.query(Task).filter_by(task_id=new_id).update({"status": "0"})
    db.session.commit()
    flash('The task was marked as complete. Nice.')
    return redirect(url_for('tasks'))


@app.route('/reopen/<int:task_id>/')
@login_required
def reopen(task_id):
    """Mark given task as open."""
    new_id = task_id
    db.session.query(Task).filter_by(task_id=new_id).update({"status": "1"})
    db.session.commit()
    flash('The task was marked as open.')
    return redirect(url_for('tasks'))


@app.route('/delete/<int:task_id>/')
@login_required
def delete_entry(task_id):
    """Delete given task."""
    new_id = task_id
    db.session.query(Task).filter_by(task_id=new_id).delete()
    db.session.commit()
    flash('The task was deleted. Why not add a new one?')
    return redirect(url_for('tasks'))


@app.route('/register/', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    error = None
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User(
                form.name.data,
                form.email.data,
                form.password.data,
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Thanks for regeistering. Please login.')
            return redirect(url_for('login'))
    return render_template('register.html', form=form, error=error)
