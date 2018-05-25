from project import db
from project.models import Task, User
from datetime import date

# create a database and the db table
db.create_all()

# insert data (if not done)
db.session.add(
    User('admin', 'ad@min.com', 'admin', 'admin')
)
db.session.add(
    Task("Finish this tutorial",
         date(2018, 9, 22), 10, date(2018, 9, 22), 1, 1)
)
db.session.add(
    Task("Finish Real Python",
         date(2018, 1, 3), 10, date(2018, 1, 3), 1, 1)
)

# commit the changes
db.session.commit()
