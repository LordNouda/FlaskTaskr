import os
from unittest import TestCase, main

from project import app, db, bcrypt
from project._config import basedir
from project.models import User

TEST_DB = 'test.db'


class UserTests(TestCase):
    """Run User related tests."""

    ###########################################################################
    # #  setup and teardown                                                 # #
    ###########################################################################

    def setUp(self):
        """Set up test scenario."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()

        self.assertEqual(app.debug, False)

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
            ),
            follow_redirects=True
        )

    def logout(self):
        """Logout the user."""
        return self.app.get('/logout/', follow_redirects=True)

    def create_user(self, name, email, password):
        """Create a user."""
        new_user = User(
            name=name,
            email=email,
            password=bcrypt.generate_password_hash(password)
        )
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
    # #  user tests                                                         # #
    ###########################################################################

    def test_user_can_register(self):
        """Test setup of user entry in database."""
        new_user = User(
            "michael",
            "michael@mherman.org",
            bcrypt.generate_password_hash('michaelherman')
        )
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
            b'Please sign in to access your task list',
            response.data
        )

    def test_users_cannot_login_unless_registered(self):
        """Test if unregistered users cannot log in."""
        response = self.login('foo', 'bar')
        self.assertIn(
            b'Please sign in to access your task list',
            response.data
        )

    def test_user_can_login(self):
        """Test if user can successfully login."""
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        response = self.login('Michael', 'python')
        self.assertIn(b'Welcome!', response.data)

    def test_invalid_form_data(self):
        """Test if bad data prevents login."""
        self.register('Michael', 'michael@realpython.com', 'python', 'python')
        response = self.login('alert("alert box!");', 'foo')
        self.assertIn(b'Invalid username or password.', response.data)

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
            b'That username and/or email already exist',
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
        self.assertIn(
            b'Please sign in to access your task list',
            response.data
        )

    def test_duplicate_user_registration_throws_error(self):
        """Test if duplicate user registration throws an error."""
        self.register(
            'Fletcher', 'fletcher@realpython.com', 'python101', 'python101'
        )
        response = self.register(
            'Fletcher', 'fletcher@realpython.com', 'python101', 'python101'
        )
        self.assertIn(
            b'That username and/or email already exist.',
            response.data
        )

    def test_user_login_field_errors(self):
        """Test is user login field error throws an error."""
        response = self.app.post(
            '/',
            data=dict(
                name='',
                password='python101',
            ),
            follow_redirects=True
        )
        self.assertIn(b'This field is required.', response.data)

    def test_string_representation_of_the_user_object(self):
        """Test if the __repr__ method works as expected."""
        db.session.add(User("Johnny", "john@doe.com", "johnny"))
        db.session.commit()
        users = db.session.query(User).all()
        for user in users:
            self.assertEqual(user.name, 'Johnny')

    def test_default_user_role(self):
        """Test if a new user is created with role 'user'."""
        db.session.add(User("Johnny", "john@doe.com", "johnny"))
        db.session.commit()
        users = db.session.query(User).all()
        for user in users:
            self.assertEqual(user.role, 'user')

    def test_task_template_displays_logged_in_user_name(self):
        """Test if the user name is displayed correctly."""
        self.register(
            'Fletcher', 'fletcher@realpython.com', 'python101', 'python101'
        )
        self.login('Fletcher', 'python101')
        response = self.app.get('/tasks/', follow_redirects=True)
        self.assertIn(b'Fletcher', response.data)


if __name__ == '__main__':
    main()
