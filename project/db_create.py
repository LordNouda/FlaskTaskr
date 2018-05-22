from views import db
from models import Task
from datetime import date

# create a database and the db table
db.create_all()

# insert data
db.session.add(Task("Finish this tutorial", date(2018, 9, 22), 10, 1))
db.session.add(Task("Finish Real Python", date(2018, 1, 3), 10, 1))

# commit the changes
db.session.commit()
