import graphene

from datetime import datetime
from werkzeug.exceptions import InternalServerError
from ..utils.util import parse_kwargs
from ..models.model import db
from ..models.auth_model import AuthDB
from ..models.user_vocab_model import UserVocabDB, UserVocab
from ..models.vocab_model import VocabDB, Vocab
from ..models.user_model import UserDB
from flask_graphql_auth import (
    get_jwt_identity,
    mutation_jwt_required,
)


# TODO: refector models into some where else
class VocabListHeader(graphene.ObjectType):
    name = graphene.String()
    list_id = graphene.Int()
    edition = graphene.DateTime()
    vocab_ids = graphene.List(graphene.String)


class VocabUserVocab(Vocab, UserVocab):
    def from_vocab_and_user_vocab(self, vocab, user_vocab):
        if vocab is not None:
            self.vocab_id = vocab.vocab_id
            self.edition = vocab.edition
            self.list_ids = vocab.list_ids
            self.vocab = vocab.vocab
            self.type = vocab.type
            self.main_translation = vocab.main_translation
            self.other_translation = vocab.other_translation
            self.main_sound = vocab.main_sound
            self.other_sound = vocab.other_sound
            self.english_translation = vocab.english_translation
            self.confusing_word_id = vocab.confusing_word_id
            self.mem_tips = vocab.mem_tips
            self.example_sentences = vocab.example_sentences
        if user_vocab is not None:
            # id = graphene.Int()
            # self.uuid = graphene.UUID()
            # self.vocab_id = graphene.String()
            self.nth_word = user_vocab.nth_word
            self.nth_appear = user_vocab.nth_appear
            self.edited_meaning = user_vocab.edited_meaning
            self.book_marked = user_vocab.book_marked
            self.question_mark = user_vocab.question_mark
            self.star_mark = user_vocab.star_mark
            self.pin_mark = user_vocab.pin_mark
            self.added_mark = user_vocab.added_mark
        return self


class ListDownloadMutation(graphene.Mutation):
    """
    INPUT: (uuid, access_token, list_id, ...)
    DO: get all vocab from list_id
    OUTPUT: (vocabs | access_token in database), (None | access_token in database)

    EXAMPLE INPUT:
    mutation {
        listDownload(uuid: "uuid", accessToken: "token", listId: 0) {
         vocabs
        }
    }
    """
    class Arguments:
        uuid = graphene.String(required=True)
        access_token = graphene.String(required=True)
        list_id = graphene.Int(required=True)

    header = graphene.Field(VocabListHeader)
    vocabs = graphene.List(VocabUserVocab)

    @staticmethod
    @mutation_jwt_required
    def mutate(parent, info, **kwargs):
        kwargs = parse_kwargs(kwargs)

        if ("jwt_error" in kwargs):
            raise Exception("400|[Warning] JWT incorrect")

        if (get_jwt_identity() != kwargs["uuid"]):
            raise Exception("400|[Warning] incorrect uuid")
        auth_db = AuthDB.get(kwargs["uuid"])

        if (auth_db is None):
            raise InternalServerError(
                "[Error] for some reason user {} doesn't have auth database".
                format(kwargs["user_name"] if "user_name" in
                       kwargs else kwargs["uuid"]))
        else:
            list_header = {
                0: {
                    "name": "list_name",
                    "list_id": 0,
                    "edition":
                    datetime.fromisoformat("2021-01-23T02:26:15.196899"),
                    "vocab_ids": {"vocab_id", "0", "1"}
                },
                1: {
                    "name": "list_name",
                    "list_id": 1,
                    "edition":
                    datetime.fromisoformat("2017-01-01T12:30:59.000000"),
                    "vocab_ids": {"vocab_id", "0"}
                },
            }
            header_data = list_header.get(kwargs["list_id"])

            # get vocab data
            vocab_dbs = VocabDB.gets(header_data.get("vocab_ids", {}))
            vocab_ids = (vocab_db.vocab_id for vocab_db in vocab_dbs)

            # get user vocab data
            user_vocab_dbs = (UserVocabDB.get_by_uuid_vocab_id(
                kwargs["uuid"], vocab_id) for vocab_id in vocab_ids)

            # combine them
            combined = (
                VocabUserVocab().from_vocab_and_user_vocab(
                    vocab_db, user_vocab_db)
                for vocab_db, user_vocab_db in zip(vocab_dbs, user_vocab_dbs))

            return ListDownloadMutation(header=VocabListHeader(
                name=header_data.get("name"),
                list_id=header_data.get("list_id"),
                edition=header_data.get("edition"),
                vocab_ids=header_data.get("vocab_ids")),
                                        vocabs=list(combined))
