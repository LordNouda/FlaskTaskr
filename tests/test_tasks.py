import os
from unittest import TestCase, main

from project import app, db
from project._config import basedir
from project.models import Task, User

TEST_DB = 'test.db'


class TasksTests(TestCase):
    """Run Task related tests."""

    ###########################################################################
    # #  setup and teardown                                                 # #
    ###########################################################################

    def setUp(self):
        """Set up test scenario."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        """Tear down test scenario."""
        db.session.remove()
        db.drop_all()

    ###########################################################################
    #                                                                        ##
    #     helper methods                                                     ##
    #                                                                        ##
    #     #   # ##### #     ####  ##### ####   ####                          ##
    #     #   # #     #     #   # #     #   # #                              ##
    #     ##### ###   #     ####  ###   ####   ###                           ##
    #     #   # #     #     #     #     #  #      #                          ##
    #     #   # ##### ##### #     ##### #   # ####                           ##
    #                                                                        ##
    ###########################################################################

    def login(self, name, password):
        """Login the user via the Flask app."""
        return self.app.post(
            '/',
            data=dict(
                name=name,
                password=password
            ),
            follow_redirects=True
        )

    def register(self, name, email, password, confirm):
        """Register a new user."""
        return self.app.post(
            'register/',
            data=dict(
                name=name,
                email=email,
                password=password,
                confirm=confirm
            ),
            follow_redirects=True
        )

    def logout(self):
        """Logout the user."""
        return self.app.get('logout/', follow_redirects=True)

    def create_user(self, name, email, password):
        """Create a user."""
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

    def create_task(self):
        """Create a new task."""
        return self.app.post('add/', data=dict(
            name='Go to the bank',
            due_date='02/05/2015',
            priority='1',
            posted_date='02/04/2015',
            status='1'
        ), follow_redirects=True)

    def create_admin_user(self):
        """Create an admin role user.."""
        new_user = User(
            name='Superman',
            email='admin@realpython.com',
            password='allpowerful',
            role='admin'
        )
        db.session.add(new_user)
        db.session.commit()

    ###########################################################################
    # #  task tests                                                         # #
    ###########################################################################

    def test_logged_in_users_can_access_tasks_page(self):
        """Test if logged in users can access tasks page."""
        self.register(
            'Fletcher', 'fletcher@realpython.com', 'python101', 'python101'
        )
        self.login('Fletcher', 'python101')
        response = self.app.get('tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add a new task:', response.data)

    def test_not_logged_in_users_cannot_access_tasks_page(self):
        """Test fi not logged in users are redirected to main page."""
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn(b'You need to login first.', response.data)

    def test_users_can_add_tasks(self):
        """Test if users can create tasks."""
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(
            b'New entry was successfully posted. Thanks.', response.data
        )

    def test_users_cannot_add_tasks_when_error(self):
        """Test if errors during task creation are caught."""
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.post('add/', data=dict(
            name='Go to the bank',
            due_date='',
            priority='1',
            posted_date='02/05/2014',
            status='1'
        ), follow_redirects=True)
        self.assertIn(b'This field is required.', response.data)

    def test_users_can_complete_tasks(self):
        """Test if users can check tasks as completed."""
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertIn(b'The task is complete. Nice.', response.data)

    # def test_users_can_reopen_tasks(self):
    #     """Test if users can check tasks as open."""
    #     self.create_user('Michael', 'michael@realpython.com', 'python')
    #     self.login('Michael', 'python')
    #     self.app.get('/tasks/', follow_redirects=True)
    #     self.create_task()
    #     response = self.app.get('/reopen/1/', follow_redirects=True)
    #     self.assertIn(b'The task was marked as open.', response.data)

    def test_users_can_delete_tasks(self):
        """Test if users can delete tasks."""
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get("delete/1/", follow_redirects=True)
        self.assertIn(b'The task was deleted.', response.data)

    def test_users_cannot_complete_tasks_that_are_not_created_by_them(self):
        """Test if users cannot complete other's tasks."""
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user('Fletcher', 'fletcher@realpython.com', 'python101')
        self.login('Fletcher', 'python101')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertNotIn(
            b'The task is complete. Nice.', response.data
        )
        self.assertIn(
            b'You can only update tasks that belong to you.', response.data
        )

    # def test_users_cannot_reopen_tasks_that_are_not_created_by_them(self):
    #     """Test if users cannot reopen other's tasks."""
    #     self.create_user('Michael', 'michael@realpython.com', 'python')
    #     self.login('Michael', 'python')
    #     self.app.get('tasks/', follow_redirects=True)
    #     self.create_task()
    #     self.logout()
    #     self.create_user('Fletcher', 'fletcher@realpython.com', 'python101')
    #     self.login('Fletcher', 'python101')
    #     self.app.get('tasks/', follow_redirects=True)
    #     response = self.app.get("reopen/1/", follow_redirects=True)
    #     self.assertNotIn(
    #         b'The task was marked as open.', response.data
    #     )
    #     self.assertIn(
    #         b'You can only update tasks that belong to you.', response.data
    #     )

    def test_users_cannot_delete_tasks_that_are_not_created_by_them(self):
        """Test if users cannot delete tasks that are not theirs."""
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user('Fletcher', 'fletcher@realpython.com', 'python101')
        self.login('Fletcher', 'python101')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("delete/1/", follow_redirects=True)
        self.assertIn(
            b'You can only delete tasks that belong to you.', response.data
        )

    def test_admin_users_can_complete_tasks_that_are_not_created_by_them(self):
        """Test if admin users can mark all tasks as complete."""
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'allpowerful')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("complete/1/", follow_redirects=True)
        self.assertNotIn(
            b'You can only update tasks that belong to you.', response.data
        )

    def test_admin_users_can_delete_tasks_that_are_not_created_by_them(self):
        """Test if admin users can delete all tasks."""
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'allpowerful')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get("delete/1/", follow_redirects=True)
        self.assertNotIn(
            b'You can only delete tasks that belong to you.', response.data
        )

    def test_string_reprsentation_of_the_task_object(self):
        """Test if the __repr__ method works as expected."""
        from datetime import date
        db.session.add(
            Task(
                "Run around in circles",
                date(2015, 1, 22),
                10,
                date(2015, 1, 23),
                1,
                1
            )
        )
        db.session.commit()
        tasks = db.session.query(Task).all()
        for task in tasks:
            self.assertEqual(task.name, 'Run around in circles')


if __name__ == "__main__":
    main()
