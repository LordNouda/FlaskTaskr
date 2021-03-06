###############################################################################
#                                                                            ##
#     imports                                                                ##
#                                                                            ##
#     ##### #     # ####   ###  ####  #####  ####                            ##
#       #   ##   ## #   # #   # #   #   #   #                                ##
#       #   # # # # ####  #   # ####    #    ###                             ##
#       #   #  #  # #     #   # #  #    #       #                            ##
#     ##### #     # #      ###  #   #   #   ####                             ##
#                                                                            ##
###############################################################################

from datetime import datetime
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

###############################################################################
#                                                                            ##
#     configuration                                                          ##
#                                                                            ##
#      ####  ###  #   # ##### #####  ####                                    ##
#     #     #   # ##  # #       #   #                                        ##
#     #     #   # # # # ###     #   # ###                                    ##
#     #     #   # #  ## #       #   #   #                                    ##
#      ####  ###  #   # #     #####  ###                                     ##
#                                                                            ##
###############################################################################

app = Flask(__name__)
app.config.from_pyfile("_config.py")
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

# blueprints = ['users', 'tasks', 'api']
# from werkzeug.utils import import_string
# for bp_str in blueprints:
#   bp = import_string('project.' + bp_str + '.views')
#   app.register_blueprint(bp)
# this should work as well, especially with many blueprints

from project.users.views import users_blueprint
from project.tasks.views import tasks_blueprint
from project.api.views import api_blueprint

app.register_blueprint(users_blueprint)
app.register_blueprint(tasks_blueprint)
app.register_blueprint(api_blueprint)


###############################################################################
#                                                                            ##
#     routes                                                                 ##
#                                                                            ##
#     ####    ####  #    # ##### #####  ####                                 ##
#     #   #  #    # #    #   #   #     #                                     ##
#     ####   #    # #    #   #   ###    ###                                  ##
#     #  #   #    # #    #   #   #         #                                 ##
#     #   #   ####   ####    #   ##### ####                                  ##
#                                                                            ##
###############################################################################

@app.errorhandler(404)
def not_found(error):
    """something."""
    if app.debug is not True:
        now = datetime.now()
        r = request.url
        with open('error.log', 'a') as f:
            current_timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
            f.write("\n404 error at {}: {}".format(current_timestamp, r))
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """something."""
    db.session.rollback()
    if app.debug is not True:
        now = datetime.now()
        r = request.url
        with open('error.log', 'a') as f:
            current_timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
            f.write("\n500 error at {}: {}".format(current_timestamp, r))
    return render_template('500.html'), 500
