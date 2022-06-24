from sre_constants import SUCCESS
import eventlet
import datetime
import graphene
import json
import traceback

from flask import Flask, Response, request, abort, render_template, send_from_directory, current_app
from flask_graphql_auth import (
    GraphQLAuth,
    get_jwt_identity,
    query_jwt_required,
)

from werkzeug.exceptions import InternalServerError
from database import db
from project.query import Query
from project.mutation import Mutation

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

app = Flask(__name__)
# Query fields can be executed in parallel by the GraphQL engine while Mutation top-level fields MUST execute serially
# See: https://stackoverflow.com/questions/48003767/what-is-the-difference-between-mutation-and-query
schema = graphene.Schema(query=Query, mutation=Mutation, auto_camelcase=True)

def init_app():
    print("Init GraphQLAuth...")
    return GraphQLAuth(app)

def init_database():
    # importing order matters: https://stackoverflow.com/questions/11720898/flask-sqlalchemy-relationships-between-different-modules
    with app.app_context():
        print("Init SQLAlchemy...")

        # Difference Between Plain SQLAlchemy and FlaskSQLiteAlchemy
        # https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#road-to-enlightenment
        # Contextual/Thread-local Sessions: https://docs.sqlalchemy.org/en/14/orm/contextual.html
        # You have to commit the session, but you don’t have to remove it at the end of the request, Flask-SQLAlchemy does that for you.
        # SQLAlchemy gives you a preconfigured scoped session called session
        db.init_app(app)

        # see https://stackoverflow.com/questions/46540664/no-application-found-either-work-inside-a-view-function-or-push-an-application
        # This line should be put after all database models initialized.
        # It is fine to be here because of import chains [app.py -> project.mutation/query -> models]
        print("Creating Database...")
        db.create_all()

# LOAD ARGUMENT
print("Parsing Arguments...")
import argparse
parser = argparse.ArgumentParser(prog="python app.py", description="Launch backend of DeepVocab")
parser.add_argument('--version', action='version', version='%(prog)s v0.1')
# parser.add_argument('--verbose', '-v', dest='verbose', action='count', default=0) # -vvv
parser.add_argument('--port', '-p', dest='port', default=5000, type=int, nargs='?', help='port number, default 5000')
parser.add_argument('--host', dest='host', default='0.0.0.0', type=str, nargs='?', help='host address, default 0.0.0.0')
# args = parser.parse_args()
# compatible with gunicorn (https://stackoverflow.com/questions/32802303/python-flask-gunicorn-error-unrecognized-arguments)
args, unknown = parser.parse_known_args()
print(vars(args))

# LOAD .ENV
print("Parsing .env...")
import os
from dotenv import load_dotenv
load_dotenv()
app.config["FLASK_APP"] = os.getenv("FLASK_APP")
app.config["BACKEND_SECRET_KEY"] = os.getenv("BACKEND_SECRET_KEY")
app.config["DOWNLOAD_FOLDER"] = os.getenv("DOWNLOAD_FOLDER")
app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER")
app.config["CSV_PATH"] = os.getenv("CSV_PATH")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_TOKEN_ARGUMENT_NAME"] = os.getenv("JWT_TOKEN_ARGUMENT_NAME")
app.config["JWT_ERROR"] = os.getenv("JWT_ERROR")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES"))
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES"))
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS") == 'True'
app.config["SQLALCHEMY_ECHO"] = os.getenv("SQLALCHEMY_ECHO") == 'True'
app.config["FULL_CHAIN"] = os.getenv("FULL_CHAIN")
app.config["PRIVATE_KEY"] = os.getenv("PRIVATE_KEY")
app.config["SMTP_SERVER"] = os.getenv("SMTP_SERVER")
app.config["SMTP_PORT"] = int(os.getenv("SMTP_PORT"))
app.config["SMTP_USER"] = os.getenv("SMTP_USER")
app.config["SMTP_PASSWORD"] = os.getenv("SMTP_PASSWORD")

print(app.config)
ssl_context=(app.config["FULL_CHAIN"], app.config["PRIVATE_KEY"]) if app.config["FULL_CHAIN"] is not None and app.config["PRIVATE_KEY"] is not None else None

auth = init_app()
init_database()

def get_query(request):
    if (request.data == None or len(request.data) < 1):
        raise Exception(
            "404|[Warning] Invalid Request, data too short. request.data={}, len={}"
            .format(request.data, len(request.data)))

    data = None
    try:
        data = json.loads(
            request.data)  # turn unformatted json into json format
        
        current_app.logger.info(bcolors.BOLD + "[DEBUG] json = {}".format(data) + bcolors.ENDC)
    except:
        raise Exception(
            "404|[Warning] Invalid Request, can't parse to json. request.data={}, len={}"
            .format(request.data, len(request.data)))
    return data


def parse_result(result):
    errors = result.errors
    extensions = result.extensions
    invalid = result.invalid
    to_dict = result.to_dict()

    try:
        status = 200 if errors is None else int(
            errors[0].message.split("|")[0])
    except ValueError:
        raise InternalServerError(
            "Cannot parse error to string. That means this is not a client error."
        )
    except AttributeError:
        raise errors[0]
    error_message = None if status == 200 else errors[0].message.split("|")[1]
    if error_message != None:
        current_app.logger.info(bcolors.BOLD +
              "[DEBUG] error = {}, error code = {}, message = {}".format(
                  errors, status, error_message) + bcolors.ENDC)
    if result.data is None:
        error_message = "Invalid request"
        status = 404
    return extensions, invalid, to_dict, error_message, status


def json_dump(data,
              extensions,
              error_message,
              path=None,
              error_extensions=None):
    if extensions is None and error_message is None:
        return json.dumps(data)
    return json.dumps({
        "data":
        data,
        "extensions":
        extensions,
        "errors": [
            {
                "message": error_message,
                "path": path,
                "extensions": error_extensions
            },
        ] if error_message is not None else None,
        # see: https://www.apollographql.com/docs/apollo-server/data/errors/
    })

@app.route("/test", methods=["POST"])
def test():
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route("/graphql", methods=["POST"])
def graphql():
    try:
        data = get_query(request)

        result = schema.execute(
            data["query"],
            variables=data["variables"] if "variables" in data else None,
            operation_name=data["operationName"]
            if "operationName" in data else None)

        extensions, invalid, to_dict, error_message, status = parse_result(
            result)
        json_result = json_dump(result.data, extensions, error_message)
        # print("[DEBUG] result = {}".format(json_result))

        return Response(response=json_result,
                        status=status,
                        mimetype='text/json')
    except:
        traceback.print_exc()
        abort(500)


@app.route(
    "/secure_download/<string:{}>/<uuid:uuid>/<int:list_id>/<path:filename>".
    format(app.config["JWT_TOKEN_ARGUMENT_NAME"]),
    methods=["GET"])
@query_jwt_required
def secure_download(**kwargs):
    """
    string: (default) accepts any text without a slash
    int: accepts positive integers
    float: accepts positive floating point values
    path: like string but also accepts slashes
    uuid: accepts UUID strings
    """
    try:
        result = schema.execute("""mutation {{
                listDownload(uuid: \"{uuid}\", accessToken: \"{access_token}\", listId: {list_id}) {{
                    header {{
                        name,
                        listId,
                        edition,
                        vocabIds
                    }},
                    vocabs {{
                        vocabId
                        edition
                        listIds
                        vocab
                        type
                        mainTranslation
                        otherTranslation
                        mainSound
                        otherSound
                        englishTranslation
                        confusingWords
                        memTips
                        exampleSentences
                        nthWord
                        nthAppear
                        editedMeaning
                        bookMarked
                        questionMark
                        starMark
                        pinMark
                        addedMark
                        markColors {{
                            id
                            vocabId
                            uuid
                            index
                            color
                            time
                        }}
                    }}
                }}
            }}""".format(uuid=kwargs["uuid"],
                         access_token=kwargs["access_token"],
                         list_id=kwargs["list_id"]))
        current_app.logger.info("[ListDownloadedMutation] start parsing result")
        extensions, invalid, to_dict, error_message, status = parse_result(
            result)
        # print("listDownload = {}".format(result.data["listDownload"]))

        current_app.logger.info("[ListDownloadedMutation] start dump result")
        # json_result = json_dump(result.data, extensions, error_message)
        json_result = json_dump(result.data["listDownload"], None, None)
        # print("[DEBUG] result = {}".format(json_result))


        current_app.logger.info("[ListDownloadedMutation] returning")
        # TODO: consider using generator, see: https://stackoverflow.com/questions/12166970/in-python-using-flask-how-can-i-write-out-an-object-for-download
        return Response(response=json_result,
                        status=status,
                        mimetype='text/json')
    except:
        traceback.print_exc()
        abort(500)

if __name__ == "__main__":
    print(bcolors.WARNING + "You are in DEBUG mode! Don't use it as production!")
    print(bcolors.ENDC)
    # if you want to use 80, see: https://gist.github.com/ejustinmklam/f13bb53be9bb15ec182b4877c9e9958d
    # load_dotenv=False because we want to load earlier than this
    app.run(host=args.host, port=args.port, debug=True, load_dotenv=False, ssl_context=ssl_context) # this line must execute after @app.route
else:
    eventlet.monkey_patch()
    print(bcolors.WARNING + "You are in PRODUCTION mode! Make sure you have correct URIs.")
    print(bcolors.ENDC)
    # app.run will be execute in wsgi.py