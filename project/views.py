import json

from werkzeug.exceptions import InternalServerError
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
    query = get_query(request)

    result = schema.execute(query)

    extensions, invalid, to_dict, error_message, status = parse_result(result)
    json_result = json_dump(result.data, extensions, error_message)
    print("[DEBUG] result = {}".format(json_result))

    return Response(response=json_result, status=status, mimetype='text/json')


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
                      confusingWordId
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

    extensions, invalid, to_dict, error_message, status = parse_result(result)
    print("listDownload = {}".format(result.data["listDownload"]))

    # json_result = json_dump(result.data, extensions, error_message)
    json_result = json_dump(result.data["listDownload"], None, None)
    print("[DEBUG] result = {}".format(json_result))

    return Response(response=json_result, status=status, mimetype='text/json')


# @app.route("/download/<path:filename>", methods=["GET"])
# def download(**kwargs):
#     # print("Sending file: {}".format(
#     #     os.path.join(current_app.root_path, app.config['DOWNLOAD_FOLDER'],
#     #                  filename)))
#     # return send_from_directory(directory=os.path.join(
#     #     current_app.root_path, app.config['DOWNLOAD_FOLDER']),
#     #                            filename=filename,
#     #                            as_attachment=False)
#     def generator(list_id):
#         list_header = {
#             0: {"vocab_id", "0"},
#             1: {"1"},
#         }
#         for vocab_id in list_header.get(list_id, {}):
#             print(dir(VocabDB.get(vocab_id)))
#             print(VocabDB.get(vocab_id).to_json())
#             yield VocabDB.get(vocab_id).to_graphql_object().vocab_id

#     # see: https://stackoverflow.com/questions/12166970/in-python-using-flask-how-can-i-write-out-an-object-for-download
#     return Response(response=generator(0),
#                     mimetype="text/plain",
#                     headers={
#                         "Content-Disposition":
#                         "attachment;filename={filename}".format(
#                             filename=kwargs["filename"])
#                     })