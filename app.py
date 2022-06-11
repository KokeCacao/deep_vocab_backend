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
from database import args, db
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
    # file download stuff
    app.config['DOWNLOAD_FOLDER'] = "download/"
    app.config['UPLOAD_FOLDER'] = "upload/"

    # flask-JWT stuff
    app.config["JWT_SECRET_KEY"] = "DeepVocab: coded by Koke_Cacao on 2021/01/01. Yah, this was how I spend my new year. 许愿有个女朋友".encode("utf-8")
    app.config["JWT_TOKEN_ARGUMENT_NAME"] = "access_token"
    app.config["JWT_ERROR"] = "jwt_error"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(minutes=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = datetime.timedelta(days=30 * 12 * 4)
    auth = GraphQLAuth(app)
    return auth

def init_database():
    # importing order matters: https://stackoverflow.com/questions/11720898/flask-sqlalchemy-relationships-between-different-modules
    with app.app_context():
        # database stuff
        # 'sqlite:///:memory:' for memory db
        print("App Config and Init SQLAlchemy...")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + args.database
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
        app.config['SQLALCHEMY_ECHO'] = False

        # Difference Between Plain SQLAlchemy and FlaskSQLiteAlchemy
        # https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#road-to-enlightenment
        # Contextual/Thread-local Sessions: https://docs.sqlalchemy.org/en/14/orm/contextual.html
        # You have to commit the session, but you don’t have to remove it at the end of the request, Flask-SQLAlchemy does that for you.
        # SQLAlchemy gives you a preconfigured scoped session called session
        db.init_app(app)

        print("Creating Database...")
        db.create_all()

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
    return 200

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
    print(vars(args))
    print(bcolors.ENDC)
    # if you want to use 80, see: https://gist.github.com/justinmklam/f13bb53be9bb15ec182b4877c9e9958d
    app.run(host=args.host, port=args.port, debug=True) # this line must execute after @app.route
else:
    eventlet.monkey_patch()
    # override because we are running in wsgi
    # and we can't pass in params
    args.verbose = 0
    args.port = 5000
    args.host = '0.0.0.0'
    args.database = '/home/ubuntu/dev/database/deep_vocab.db'
    args.csv = '/home/ubuntu/dev/database/data.csv'
    print(bcolors.WARNING + "You are in PRODUCTION mode! Make sure you have correct URIs.")
    print(vars(args))
    print(bcolors.ENDC)