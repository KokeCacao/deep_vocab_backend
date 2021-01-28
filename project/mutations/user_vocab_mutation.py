import graphene

from werkzeug.exceptions import InternalServerError
from ..utils.util import parse_kwargs
from ..models.model import db
from ..models.auth_model import AuthDB
from ..models.user_vocab_model import UserVocab, UserVocabDB
from ..models.user_model import UserDB
from flask_graphql_auth import (
    get_jwt_identity,
    mutation_jwt_required,
)


class UserVocabMutation(graphene.Mutation):
    """
    INPUT: ([uuid, user_name], access_token, vocab_id, ...)
    DO: add or update user vocab if access_token in database
    OUTPUT: (* | access_token in database), (None | access_token in database)

    EXAMPLE INPUT:
    mutation {
        userVocab(uuid: "2d480cd1-7e8b-4040-a81e-76191e4da0e5", accessToken: "token", vocabId: "id", editedMeaning: "", bookMarked: false, questionMark: false, starMark: false, pinMark: false, addedMark: false) {
            vocabId
            nthWord
            nthAppear
            editedMeaning
        }
    }
    """
    class Arguments:
        uuid = graphene.String(required=False)
        access_token = graphene.String(required=True)
        user_name = graphene.String(required=False)
        vocab_id = graphene.String(required=True)
        edited_meaning = graphene.String(required=False)
        book_marked = graphene.Boolean(required=False)
        question_mark = graphene.Boolean(required=False)
        star_mark = graphene.Boolean(required=False)
        pin_mark = graphene.Boolean(required=False)
        added_mark = graphene.Boolean(required=False)

    vocab_id = graphene.String()
    nth_word = graphene.Int()
    nth_appear = graphene.Int()
    edited_meaning = graphene.String()
    book_marked = graphene.Boolean()
    question_mark = graphene.Boolean()
    star_mark = graphene.Boolean()
    pin_mark = graphene.Boolean()
    added_mark = graphene.Boolean()

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
            user_vocab_db = UserVocabDB.get_by_uuid_vocab_id(
                uuid=kwargs["uuid"], vocab_id=kwargs["vocab_id"])
            if user_vocab_db is None:
                user_db = UserDB.get(uuid=kwargs["uuid"])
                if (user_db is None):
                    raise InternalServerError(
                        "[Error] for some reason user {} doesn't have user database"
                        .format(kwargs["user_name"] if "user_name" in
                                kwargs else kwargs["uuid"]))
                nth_word = user_db.xp

                user_vocab_db = UserVocabDB.add(
                    uuid=kwargs["uuid"],
                    vocab_id=kwargs["vocab_id"],
                    nth_word=nth_word,
                    nth_appear=None,
                    edited_meaning=kwargs["edited_meaning"]
                    if "edited_meaning" in kwargs else None,
                    book_marked=kwargs["book_marked"]
                    if "book_marked" in kwargs else None,
                    question_mark=kwargs["question_mark"]
                    if "question_mark" in kwargs else None,
                    star_mark=kwargs["star_mark"]
                    if "star_mark" in kwargs else None,
                    pin_mark=kwargs["pin_mark"]
                    if "pin_mark" in kwargs else None,
                    added_mark=kwargs["added_mark"]
                    if "added_mark" in kwargs else None)
            else:
                filtered_kwargs = {
                    k: kwargs[k]
                    for k in [
                        "edited_meaning", "book_marked", "question_mark",
                        "star_mark", "pin_mark", "added_mark"
                    ] if k in kwargs
                }
                print("filtered kwargs = {}".format(filtered_kwargs))
                user_vocab_db = UserVocabDB.update(user_vocab_db,
                                                   **filtered_kwargs)

        db.session.commit()
        return user_vocab_db.to_graphql_object()