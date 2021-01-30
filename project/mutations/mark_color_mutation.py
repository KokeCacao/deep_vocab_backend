import graphene

from werkzeug.exceptions import InternalServerError
from ..utils.util import parse_kwargs
from ..models.model import db
from ..models.auth_model import AuthDB
from ..models.mark_color_model import ColorModel, MarkColorDB
from flask_graphql_auth import (
    get_jwt_identity,
    mutation_jwt_required,
)


class MarkColorMutation(graphene.Mutation):
    """
    INPUT: ([uuid, user_name], access_token, vocab_id, index, color, time)
    DO: add or update mark_color if access_token in database
    OUTPUT: (* | access_token in database), (None | access_token in database)

    EXAMPLE INPUT:
    mutation {
        markColor(uuid: "2d480cd1-7e8b-4040-a81e-76191e4da0e5", accessToken: "token", vocabId: "id", index: 0, color: black, time: "2021-01-23T02:26:15.196092") {
            index
            color
            time
        }
    }
    """
    # graphene.Enum.from_enum(ColorModel) can't be used twice without storing the value
    # See: https://github.com/graphql-python/graphene-sqlalchemy/issues/211
    from functools import lru_cache
    graphene.Enum.from_enum = lru_cache(maxsize=None)(graphene.Enum.from_enum)

    class Arguments:
        uuid = graphene.String(required=False)
        access_token = graphene.String(required=True)
        user_name = graphene.String(required=False)
        vocab_id = graphene.String(required=True)
        index = graphene.Int(required=True)
        color = graphene.Enum.from_enum(ColorModel)(required=True)
        time = graphene.DateTime(required=True)

    vocab_id = graphene.String()
    index = graphene.Int()
    color = graphene.Enum.from_enum(ColorModel)()
    time = graphene.DateTime()

    @staticmethod
    @mutation_jwt_required
    def mutate(parent, info, **kwargs):
        def valid_kwargs(kwargs):
            return ("uuid" in kwargs and "user_name" not in kwargs) or (
                "uuid" not in kwargs and "user_name" in kwargs)

        if not valid_kwargs(kwargs):
            raise Exception("400|[Warning] invalid kwargs combinations")
        kwargs = parse_kwargs(kwargs)

        if ("jwt_error" in kwargs):
            raise Exception("400|[Warning] JWT incorrect")

        auth_db = None
        if "uuid" in kwargs:
            if (get_jwt_identity() != kwargs["uuid"]):
                raise Exception("400|[Warning] incorrect uuid")
            auth_db = AuthDB.get(kwargs["uuid"])
        elif "user_name" in kwargs:
            auth_db = AuthDB.get_by_user_name(kwargs["user_name"])
            if (get_jwt_identity() != auth_db.uuid):
                raise Exception("400|[Warning] incorrect uuid")

        if (auth_db is None):
            raise InternalServerError(
                "[Error] for some reason user {} doesn't have auth database".
                format(kwargs["user_name"] if "user_name" in
                       kwargs else kwargs["uuid"]))
        else:
            index = kwargs["index"]
            # make sure index is >= 0
            if index < 0: raise Exception("400|[Warning] index < 0")

            # make sure index-1 already exist in database or index=0
            if index != 0 and MarkColorDB.get_by_uuid_vocab_id_index(
                    auth_db.uuid, kwargs["vocab_id"], index - 1) == None:
                raise Exception(
                    "400|[Warning] index-1 does not exist in database")

            # if index already exist in database, edit such entry, return such entry
            mark_color_db = MarkColorDB.get_by_uuid_vocab_id_index(
                auth_db.uuid, kwargs["vocab_id"], index)
            if mark_color_db != None:
                mark_color_db = MarkColorDB.update(mark_color_db,
                                                   color=kwargs["color"],
                                                   time=kwargs["time"])
                db.session.commit()
                return mark_color_db.to_graphql_object()

            # else create new entry
            mark_color_db = MarkColorDB.add(uuid=auth_db.uuid,
                                            vocab_id=kwargs["vocab_id"],
                                            index=kwargs["index"],
                                            color=kwargs["color"],
                                            time=kwargs["time"])

        db.session.commit()
        return mark_color_db.to_graphql_object()