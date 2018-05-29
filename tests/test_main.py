import os
from unittest import TestCase, main

from project import app, db
from project._config import basedir
from project.models import User

TEST_DB = 'test.db'


class MainTests(TestCase):
    """docstring for MainTests."""

    ###########################################################################
    #                                                                        ##
    #     setup and teardown                                                 ##
    #                                                                        ##
    #      #### ##### ##### #   # ####                                       ##
    #     #     #       #   #   # #   #                                      ##
    #      ###  ###     #   #   # ####                                       ##
    #         # #       #   #   # #                                          ##
    #     ####  #####   #    ###  #                                          ##
    #                                                                        ##
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

    ###########################################################################
    #                                                                        ##
    #     tests                                                              ##
    #                                                                        ##
    #     ##### #####  #### #####  ####                                      ##
    #       #   #     #       #   #                                          ##
    #       #   ###    ###    #    ###                                       ##
    #       #   #         #   #       #                                      ##
    #       #   ##### ####    #   ####                                       ##
    #                                                                        ##
    ###########################################################################

    def test_404_error(self):
        """404."""
        response = self.app.get('/this-route-does-not-exist/')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Sorry. There\'s nothing here.', response.data)

    def test_500_error(self):
        """500."""
        bad_user = User(
            name='Jeremy',
            email='jeremy@realpython.com',
            password='django'
        )
        db.session.add(bad_user)
        db.session.commit()
        try:
            response = self.login('Jeremy', 'django')
            self.assertEqual(response.status_code, 500)
            self.assertIn(b'Something went terribly wrong.', response.data)
        except ValueError:
            pass

    def test_index(self):
        """Ensure flask was set up correctly."""
        response = self.app.get('/', content_type='html/text')
        self.assertEqual(200, response.status_code)


if __name__ == '__main__':
    main()
