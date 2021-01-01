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
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

import graphene
from project.query import Query
from project.mutation import Mutation
schema = graphene.Schema(query=Query, mutation=Mutation, auto_camelcase=True)

# We need to make sure Flask knows about its views before we run
# the app, so we import them. We could do it earlier, but there's
# a risk that we may run into circular dependencies, so we do it at the
# last minute here.
from project.views import *
