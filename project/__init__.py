#  A general utility script for Flask applications.

#   Provides commands from Flask, extensions, and the application. Loads the
#   application defined in the FLASK_APP environment variable, or from a
#   wsgi.py file. Setting the FLASK_ENV environment variable to 'development'
#   will enable debug mode.

#     $ export FLASK_APP=main.py
#     $ export FLASK_ENV=development
#     $ flask run
# or run flask using `FLASK_APP=main.py FLASK_ENV=development flask run`

# flask stuff
from flask import Flask
from app import args  # app here refers to app.py, but Flask()
# app = None
# try:
app = Flask(__name__)
# except Exception as e:
#     if not ("|" in e.message and e.message.split("|")[0].isdigit()):
#         print("nonononononononononononononono")
#         raise e
#     pass

# file download stuff
app.config['DOWNLOAD_FOLDER'] = "download/"
app.config['UPLOAD_FOLDER'] = "upload/"

# flask-JWT stuff
from flask_graphql_auth import GraphQLAuth
app.config[
    "JWT_SECRET_KEY"] = "DeepVocab: coded by Koke_Cacao on 2021/01/01. Yah, this was how I spend my new year. 许愿有个女朋友".encode(
        "utf-8")
app.config["JWT_TOKEN_ARGUMENT_NAME"] = "access_token"
app.config["JWT_ERROR"] = "jwt_error"
import datetime
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(minutes=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = datetime.timedelta(days=30 * 12 * 4)

auth = GraphQLAuth(app)

import graphene

# importing order matters: https://stackoverflow.com/questions/11720898/flask-sqlalchemy-relationships-between-different-modules
with app.app_context():
    from .models.model import db
    from .query import Query
    from .mutation import Mutation
    print("Creating Database...")
    db.create_all()

from .query import Query
from .mutation import Mutation
# Query fields can be executed in parallel by the GraphQL engine while Mutation top-level fields MUST execute serially
# See: https://stackoverflow.com/questions/48003767/what-is-the-difference-between-mutation-and-query
schema = graphene.Schema(query=Query, mutation=Mutation, auto_camelcase=True)

# We need to make sure Flask knows about its views before we run
# the app, so we import them. We could do it earlier, but there's
# a risk that we may run into circular dependencies, so we do it at the
# last minute here.
from .views import *
