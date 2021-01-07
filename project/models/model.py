# database stuff
from flask_sqlalchemy import SQLAlchemy  # instead of `from flask.ext.sqlalchemy import SQLAlchemy`
from .. import app


class SQLiteAlchemy(SQLAlchemy):
    def apply_driver_hacks(self, app, info, options):
        options.update({'echo': True})
        super(SQLiteAlchemy, self).apply_driver_hacks(app, info, options)


# database stuff
# 'sqlite:///:memory:' for memory db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLiteAlchemy(app)
db.init_app(app)

# see https://stackoverflow.com/questions/46540664/no-application-found-either-work-inside-a-view-function-or-push-an-application
# This line should be put after all database models
# with app.app_context():
#     print("Creating Database...")
#     db.create_all()