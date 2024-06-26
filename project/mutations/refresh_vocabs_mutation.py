import graphene

from ..utils.util import parse_kwargs, check_jwt_with_uuid
from ..models.mark_color_model import ColorModel, MarkColorDB
from ..models.vocab_model import VocabDB
from ..models.mark_color_model import MarkColorDB
from ..models.user_vocab_model import UserVocabDB
from database import db
from ..models.model import Vocab
from flask_graphql_auth import (
    get_jwt_identity,
    mutation_jwt_required,
)


class RefreshVocabMutation(graphene.Mutation):
    """
    INPUT: (uuid, access_token, client_vocab_refresh_time)
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
                      markColors {
                          id
                          vocabId
                          uuid
                          index
                          color
                          time
                      }
            }
        }
    }
    """
    # TODO: if you optimize your mutation sturcture, this might not be nesscary
    from functools import lru_cache
    graphene.Enum.from_enum = lru_cache(maxsize=None)(graphene.Enum.from_enum)

    class Arguments:
        uuid = graphene.String(required=True)
        access_token = graphene.String(required=True)
        client_vocab_refresh_time = graphene.DateTime(
            required=False)  # TODO: actually store this variable

    # vocab = graphene.Field(Vocab)
    vocabs = graphene.List(Vocab)

    @staticmethod
    @mutation_jwt_required
    def mutate(parent, info, **kwargs):
        kwargs = parse_kwargs(kwargs)
        auth_db, uuid = check_jwt_with_uuid(kwargs, get_jwt_identity())

        user_vocab_dbs = UserVocabDB.get_by_uuid_after_now(
            uuid, sorted=True, with_for_update=True, erase_cache=True)

        selected_vocab_id = [
            user_vocab_db.vocab_id for user_vocab_db in user_vocab_dbs
        ]

        # add nth_appear
        for user_vocab_db in user_vocab_dbs:
            UserVocabDB.update(user_vocab_db,
                               nth_appear=user_vocab_db.nth_appear + 1)

        # TODO: if client only wants vocabId, return here, else continue
        selected_vocab_db = VocabDB.gets(selected_vocab_id)

        db.session.commit()
        return RefreshVocabMutation(vocabs=selected_vocab_db)