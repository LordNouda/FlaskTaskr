from views import db
from models import Task  # used within db (re: flake8 F401)
from models import User  # used within db (re: flake8 F401)
# from datetime import date

# create a database and the db table
db.create_all()

# insert data (if not done)
# db.session.add(Task("Finish this tutorial", date(2018, 9, 22), 10, 1))
# db.session.add(Task("Finish Real Python", date(2018, 1, 3), 10, 1))

# commit the changes
db.session.commit()
