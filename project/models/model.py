# database stuff
from flask_sqlalchemy import SQLAlchemy  # instead of `from flask.ext.sqlalchemy import SQLAlchemy`
from .. import app
db = SQLAlchemy()
db.init_app(app)

from . import *  # import all models

# see https://stackoverflow.com/questions/46540664/no-application-found-either-work-inside-a-view-function-or-push-an-application
# This line should be put after all database generated
# with app.app_context():
#     print("Creating Database...")
#     db.create_all()