import os

# grab the folder where this script lives
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = 'flasktaskr.db'
WTF_CSRF_ENABLED = True
SECRET_KEY = 'V7EkUDirDgT8wSiTqmT2rPurysy9rtfE'
DEBUG = False

# define the full path for the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

# the database uri and other settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH
SQLALCHEMY_TRACK_MODIFICATIONS = False
