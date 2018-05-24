import os
import unittest

from views import app, db
from _config import basedir
from models import User

TEST_DB = 'test.db'


class AllTests(unittest.TestCase):
    """Run all tests."""

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
    # #  helper methods                                                     # #
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
            '/register/',
            data=dict(
                name=name,
                email=email,
                password=password,
                confirm=confirm
            )
        )

    def logout(self):
        """Logout the user."""
        return self.app.get('/logout/', follow_redirects=True)

    def create_user(self, name, email, password):
        """Create a user."""
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

    def create_task(self):
        """Create a new task."""
        return self.app.post(
            '/add/',
            data=dict(
                name='Go to the bank',
                due_date='10/08/2016',
                priority='1',
                posted_date='10/08/2016',
                status='1'
            ),
            follow_redirects=True
        )

    ###########################################################################
    # #  all tests                                                          # #
    ###########################################################################

    def test_user_setup(self):
        """Test setup of user entry in database."""
        new_user = User("michael", "michael@mherman.org", "michaelherman")
        db.session.add(new_user)
        db.session.commit()
        test = db.session.query(User).all()
        # for t in test:
        #    t.name
        assert test[0].name == "michael"
        # assert t.name == "michael"

    def test_form_is_present(self):
        """Test if form is present."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Please login to access your task list.',
            response.data
        )

    def test_users_cannot_login_unless_registered(self):
        """Test if unregistered users cannot log in."""
        response = self.login('foo', 'bar')
        self.assertIn(b'Invalid Credentials. Please try again.', response.data)

    def test_user_can_login(self):
        """Test if user can successfully login."""
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        response = self.login('Michael', 'python')
        self.assertIn(b'Welcome!', response.data)

    def test_invalid_form_data(self):
        """Test if bad data prevents login."""
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        response = self.login('alert("alert box!");', 'foo')
        self.assertIn(b'Invalid Credentials. Please try again.', response.data)

    def test_form_is_present_on_register_page(self):
        """Test if a form is present on the register page."""
        response = self.app.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Please register to access the task list.',
            response.data
        )

    def test_user_registration(self):
        """Test if users can register."""
        self.app.get('/register/', follow_redirects=True)
        response = self.register(
            'Michael', 'michael@realpython.com', 'python', 'python'
        )
        self.assertIn(b'Thanks for registering. Please login.', response.data)

    def test_user_registration_error(self):
        """Test if users receive an error if username/email already exists."""
        self.app.get('/register/', follow_redirects=True)
        self.register(
            'Michael', 'michael@realpython.com', 'python', 'python'
        )
        self.app.get('/register/', follow_redirects=True)
        response = self.register(
            'Michael', 'michael@realpython.com', 'python', 'python'
        )
        self.assertIn(
            b'That username and/or email already exists.',
            response.data
        )

    def test_logged_in_users_can_logout(self):
        """Test if logged in users can logout."""
        self.register(
            'Fletcher', 'fletcher@realpython.com', 'python101', 'python101'
        )
        self.login('Fletcher', 'python101')
        response = self.logout()
        self.assertIn(b'Goodbye!', response.data)

    def test_not_logged_in_users_can_logout(self):
        """Test if not logged in users are redirected to the main page."""
        response = self.logout()
        self.assertIn(b'Please login to access your task list.', response.data)

    def test_logged_in_users_can_access_tasks_page(self):
        """Test if logged in users can access tasks page."""
        self.register(
            'Fletcher', 'fletcher@realpython.com', 'python101', 'python101'
        )
        self.login('Fletcher', 'python101')
        response = self.app.get('/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add a new task:', response.data)

    def test_not_logged_in_users_cannot_access_tasks_page(self):
        """Test fi not logged in users are redirected to main page."""
        response = self.app.get('/tasks/', follow_redirects=True)
        self.assertIn(b'You need to login first.', response.data)

    def test_users_can_add_tasks(self):
        """Test if users can create tasks."""
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('/tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(
            b'New entry was successfully posted. Thanks.',
            response.data
        )

    def test_users_cannot_add_tasks_when_error(self):
        """Test if errors during task creation are caught."""
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('/tasks/', follow_redirects=True)
        response = self.app.post(
            '/add/',
            data=dict(
                name='Go to the bank.',
                due_date='',
                priority='1',
                posted_date='02/05/2014',
                status='1'
            ),
            follow_redirects=True
        )
        self.assertIn(b'This field is required.', response.data)

    def test_users_can_complete_tasks(self):
        """Test if users can check tasks as completed."""
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('/tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get('/complete/1/', follow_redirects=True)
        self.assertIn(b'The task was marked as complete. Nice.', response.data)

    def test_users_can_reopen_tasks(self):
        """Test if users can check tasks as open."""
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('/tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get('/reopen/1/', follow_redirects=True)
        self.assertIn(b'The task was marked as open.', response.data)

    def test_users_can_delete_tasks(self):
        """Test if users can delete tasks."""
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('/tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get('/delete/1/', follow_redirects=True)
        self.assertIn(b'The task was deleted.', response.data)

    def test_users_cannot_complete_tasks_that_are_not_created_by_them(self):
        """Test if users can not completer other's tasks."""
        self.create_user('Michael', 'michael@realpython.com', 'python')
        self.login('Michael', 'python')
        self.app.get('/tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user('Fletcher', 'fletcher@realpython.com', 'python101')
        self.login('Fletcher', 'python101')
        self.app.get('/tasks/', follow_redirects=True)
        response = self.app.get('/complete/1/', follow_redirects=True)
        self.assertNotIn(
            b'The task was marked as complete. Nice.',
            response.data
        )
# END class AllTests(unittest.TestCase)


if __name__ == '__main__':
    unittest.main()
