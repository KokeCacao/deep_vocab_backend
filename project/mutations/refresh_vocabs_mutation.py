import graphene

from werkzeug.exceptions import InternalServerError
from ..utils.util import parse_kwargs
from ..models.model import db
from ..models.auth_model import AuthDB
from ..models.mark_color_model import ColorModel, MarkColorDB
from ..models.vocab_model import VocabDB, TypeModel, Vocab
from ..models.mark_color_model import MarkColorDB
from flask_graphql_auth import (
    get_jwt_identity,
    mutation_jwt_required,
)


class RefreshVocabMutation(graphene.Mutation):
    """
    INPUT: ([uuid, user_name], access_token, client_vocab_refresh_time)
    DO: give user their vocab, record client_vocab_refresh_time to database
    OUTPUT: (vocabs | access_token in database), (None | access_token in database)

    EXAMPLE INPUT:
    mutation {
        refreshVocab(uuid: "uuid", accessToken: "access", client_vocab_refresh_time: "") {
            vocabs {
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
                # TODO: implement userVocab
            }
        }
    }
    """
    # TODO: if you optimize your mutation sturcture, this might not be nesscary
    from functools import lru_cache
    graphene.Enum.from_enum = lru_cache(maxsize=None)(graphene.Enum.from_enum)

    class Arguments:
        uuid = graphene.String(required=False)
        access_token = graphene.String(required=True)
        user_name = graphene.String(required=False)
        client_vocab_refresh_time = graphene.DateTime(
            required=False)  # TODO: actually store this variable

    # vocab = graphene.Field(Vocab)
    vocabs = graphene.List(Vocab)

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
            # TODO: set kwargs["uuid"] before using it if "uuid" not in kwargs, do the same for other mutations

            # mark_color_dict = {vocab_id: [MarkColor]}
            mark_color_dict = MarkColorDB.get_by_uuid_to_vocab_id_dict(
                kwargs["uuid"], sorted=True)

            # selected = [vocab_id that has last mark == MarkColor.black]
            selected = [
                vocab_id
                for vocab_id, mark_color_dbs in mark_color_dict.items()
                if mark_color_dbs[-1].color == ColorModel.black
            ]

            # TODO: if client only wants vocabId, return here, else continue
            selected = VocabDB.gets(selected)

        # db.session.commit()
        return RefreshVocabMutation(vocabs=selected)