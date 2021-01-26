import json
import os

from werkzeug.exceptions import InternalServerError
from . import app, schema
from .models.model import db
from flask import Flask, Response, request, abort, render_template, current_app, send_from_directory


@app.route("/graphql", methods=["POST"])
def graphql():
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

    result = schema.execute(data["query"])

    errors = result.errors
    extensions = result.extensions
    invalid = result.invalid
    to_dict = result.to_dict()

    print("[DEBUG] errors = {}".format(errors))  # TODO: test when no error

    try:
        status = 200 if errors is None else int(
            errors[0].message.split("|")[0])
    except:
        raise InternalServerError(
            "Cannot parse error to string. This is not a client error.")
    error_message = None if status == 200 else errors[0].message.split("|")[1]

    print("[DEBUG] error code = {}, message = {}".format(
        status, error_message))

    if result.data is None:
        error_message = "Invalid request"
        status = 404

    json_result = json.dumps({
        "data":
        result.data,
        "extensions":
        extensions,
        "errors": [
            {
                "message": error_message,
                "path": None,
                "extensions": None
            },
        ] if error_message is not None else
        None,  # see: https://www.apollographql.com/docs/apollo-server/data/errors/
    })
    print("[DEBUG] result = {}".format(json_result))

    return Response(response=json_result, status=status, mimetype='text/json')


# TODO: requires access token
@app.route("/download/<path:filename>", methods=["GET"])
def download(filename):
    print("Sending file: {}".format(
        os.path.join(current_app.root_path, app.config['DOWNLOAD_FOLDER'],
                     filename)))
    return send_from_directory(directory=os.path.join(
        current_app.root_path, app.config['DOWNLOAD_FOLDER']),
                               filename=filename,
                               as_attachment=False)
