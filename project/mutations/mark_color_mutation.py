import graphene

from ..utils.util import parse_kwargs, check_jwt_with_uuid
from ..models.model import db, ColorModel
from ..models.mark_color_model import MarkColorDB
from ..models.user_vocab_model import UserVocabDB
from flask_graphql_auth import (
    get_jwt_identity,
    mutation_jwt_required,
)


class MarkColorMutation(graphene.Mutation):
    """
    INPUT: (uuid, access_token, vocab_id, index, color, time)
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
        uuid = graphene.String(required=True)
        access_token = graphene.String(required=True)
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
        kwargs = parse_kwargs(kwargs)
        auth_db, uuid = check_jwt_with_uuid(kwargs, get_jwt_identity())

        index = kwargs["index"]
        # make sure index is >= 0
        if index < 0: raise Exception("400|[Warning] index < 0")

        # make sure index-1 already exist in database or index=0
        if index != 0 and MarkColorDB.get_by_uuid_vocab_id_index(
                uuid, kwargs["vocab_id"], index - 1) == None:
            raise Exception("400|[Warning] index-1 does not exist in database")

        # if index already exist in database, edit such entry, return such entry
        mark_color_db = MarkColorDB.get_by_uuid_vocab_id_index(
            uuid, kwargs["vocab_id"], index)
        if mark_color_db != None:
            mark_color_db = MarkColorDB.update(mark_color_db,
                                               color=kwargs["color"],
                                               time=kwargs["time"])
            db.session.commit()
            return MarkColorMutation(
                vocab_id=mark_color_db.vocab_id,
                index=mark_color_db.index,
                color=mark_color_db.color,
                time=mark_color_db.time,
            )

        # else create new entry
        mark_color_db = MarkColorDB.add(uuid=uuid,
                                        vocab_id=kwargs["vocab_id"],
                                        index=kwargs["index"],
                                        color=kwargs["color"],
                                        time=kwargs["time"])
        # add nth_word when needed
        if index == 0:
            user_vocab_db = UserVocabDB.gets(kwargs["vocab_id"])
            UserVocabDB.update(user_vocab_db,
                               nth_word=user_vocab_db.nth_word + 1)

        db.session.commit()
        return MarkColorMutation(
            vocab_id=mark_color_db.vocab_id,
            index=mark_color_db.index,
            color=mark_color_db.color,
            time=mark_color_db.time,
        )
