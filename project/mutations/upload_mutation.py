from datetime import datetime
import graphene
import os

from flask import current_app
from ..utils.util import parse_kwargs, check_jwt_with_uuid
from flask_graphql_auth import (
    get_jwt_identity,
    mutation_jwt_required,
)
from graphene_file_upload.scalars import Upload


class UploadMutation(graphene.Mutation):
    """
    INPUT: (uuid, access_token, file, ...)
    DO: get all vocab from list_id
    OUTPUT: (vocabs | access_token in database), (None | access_token in database)

    EXAMPLE INPUT:
    mutation {
        upload(uuid: "uuid", accessToken: "token", file: "..bytes..") {
         ok
        }
    }
    """
    class Arguments:
        uuid = graphene.UUID(required=True)
        access_token = graphene.String(required=True)
        file = Upload(required=True)

    ok = graphene.Boolean()

    @staticmethod
    @mutation_jwt_required
    def mutate(parent, info, **kwargs):
        kwargs = parse_kwargs(kwargs)
        auth_db, uuid = check_jwt_with_uuid(kwargs, get_jwt_identity())

        file_name = "{}/{}-{}.log".format(
            current_app.config["DOWNLOAD_FOLDER"], uuid,
            str(datetime.now()).replace(" ", "-"))
        os.makedirs(os.path.dirname(file_name), exist_ok=True)

        with open(file_name, "w") as file:
            file.write(kwargs["file"])

        return UploadMutation(ok=True)
