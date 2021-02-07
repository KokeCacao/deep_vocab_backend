import json

from werkzeug.exceptions import InternalServerError
from werkzeug.debug import get_current_traceback
from . import app, schema
from flask import Flask, Response, request, abort, render_template, current_app, send_from_directory
from flask_graphql_auth import (
    get_jwt_identity,
    query_jwt_required,
)


def get_query(request):
    if (request.data == None or len(request.data) < 1):
        raise Exception(
            "404|[Warning] Invalid Request, data too short. request.data={}, len={}"
            .format(request.data, len(request.data)))

    data = None
    try:
        data = json.loads(
            request.data)  # turn unformatted json into json format
        print("[DEBUG] json = {}".format(data))
    except:
        raise Exception(
            "404|[Warning] Invalid Request, can't parse to json. request.data={}, len={}"
            .format(request.data, len(request.data)))
    return data["query"]


def parse_result(result):
    errors = result.errors
    extensions = result.extensions
    invalid = result.invalid
    to_dict = result.to_dict()

    try:
        status = 200 if errors is None else int(
            errors[0].message.split("|")[0])
    except:
        raise InternalServerError(
            "Cannot parse error to string. That means this is not a client error."
        )
    error_message = None if status == 200 else errors[0].message.split("|")[1]
    if error_message != None:
        print("[DEBUG] error = {}, error code = {}, message = {}".format(
            errors, status, error_message))

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


@app.route("/graphql", methods=["POST"])
def graphql():
    try:
        query = get_query(request)

        result = schema.execute(query)

        extensions, invalid, to_dict, error_message, status = parse_result(
            result)
        json_result = json_dump(result.data, extensions, error_message)
        print("[DEBUG] result = {}".format(json_result))

        return Response(response=json_result,
                        status=status,
                        mimetype='text/json')
    except:
        get_current_traceback(skip=1,
                              show_hidden_frames=True,
                              ignore_system_exceptions=False).log()
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
        print("[ListDownloadedMutation] start parsing result")
        extensions, invalid, to_dict, error_message, status = parse_result(
            result)
        # print("listDownload = {}".format(result.data["listDownload"]))

        print("[ListDownloadedMutation] start dump result")
        # json_result = json_dump(result.data, extensions, error_message)
        json_result = json_dump(result.data["listDownload"], None, None)
        # print("[DEBUG] result = {}".format(json_result))

        print("[ListDownloadedMutation] returning")
        # TODO: consider using generator, see: https://stackoverflow.com/questions/12166970/in-python-using-flask-how-can-i-write-out-an-object-for-download
        return Response(response=json_result,
                        status=status,
                        mimetype='text/json')
    except:
        get_current_traceback(skip=1,
                              show_hidden_frames=True,
                              ignore_system_exceptions=False).log()
        abort(500)