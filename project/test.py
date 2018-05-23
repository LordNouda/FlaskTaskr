import os
import unittest

from views import app, db
from _config import basedir
from models import User

TEST_DB = 'test.db'


class AllTests(unittest.TestCase):
    """Setup and teardown."""

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


if __name__ == '__main__':
    unittest.main()
