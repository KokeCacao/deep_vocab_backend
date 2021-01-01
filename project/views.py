import json
from . import app, schema
from .models.model import db
from flask import Flask, Response, request, abort, render_template


@app.route("/graphql", methods=["POST"])
def graphql():
    if (request.data == None or len(request.data) < 1):
        abort(404,
              description="Invalid Request, request.data={}, len={}".format(
                  request.data, len(request.data)))

    data = None
    try:
        data = json.loads(
            request.data)  # turn unformatted json into json format
        print("[DEBUG] json = {}".format(data))
    except:
        print("[Error] Can't parse to json: {}".format(request.data))
        abort(404,
              description="Invalid Request, request.data={}, len={}".format(
                  request.data, len(request.data)))

    result = schema.execute(data["query"])

    json_result = json.dumps({
        "data": result.data,
        "extensions": None,
        "errors": None
    })
    print("[DEBUG] result = {}".format(json_result))

    return Response(response=json_result, status=200, mimetype='text/json')
