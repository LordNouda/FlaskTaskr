from views import db
from datetime import datetime


class Task(db.Model):
    """Create a Task."""

    __tablename__ = "tasks"

    task_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    posted_date = db.Column(db.Date, default=datetime.utcnow())
    status = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, name, due_date, priority, posted_date, status, user_id):
        """Init."""
        self.name = name
        self.due_date = due_date
        self.priority = priority
        self.posted_date = posted_date
        self.status = status
        self.user_id = user_id

    def __repr__(self):
        """Represent self."""
        return '<name {0}>'.format(self.name)


class User(db.Model):
    """Create a User."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    tasks = db.relationship('Task', backref='poster')
    role = db.Column(db.String, default='user')

    def __init__(self, name=None, email=None, password=None, role=None):
        """Init."""
        self.name = name
        self.email = email
        self.password = password
        self.role = role

    def __repr__(self):
        """Represent self."""
        return '<user {0}>'.format(self.name)
