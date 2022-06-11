import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# don't pass in the app object yet
db = SQLAlchemy()

def create_test_app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///{}/sqlite_test.db".format(os.path.dirname(os.path.abspath(__file__)))
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    print("app.config[\"SQLALCHEMY_DATABASE_URI\"]:{}".format(app.config["SQLALCHEMY_DATABASE_URI"]))
    # Dynamically bind SQLAlchemy to application
    db.init_app(app)
    app.app_context().push() # this does the binding
    return app

# you can create another app context here, say for production
def create_production_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///{}/sqlite.db".format(os.path.dirname(os.path.abspath(__file__)))
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    print("app.config[\"SQLALCHEMY_DATABASE_URI\"]:{}".format(app.config["SQLALCHEMY_DATABASE_URI"]))
    # Dynamically bind SQLAlchemy to application
    db.init_app(app)
    app.app_context().push()
    return app

from flask_testing import TestCase

class MyTest(TestCase):

    # I removed some config passing here
    def create_app(self):
        return create_test_app()

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

print("Start Testing...")
_ = MyTest()
app = _.create_app()
_.setUp()
_.tearDown()