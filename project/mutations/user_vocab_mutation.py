import graphene

from werkzeug.exceptions import InternalServerError
from ..utils.util import parse_kwargs, check_jwt_with_uuid
from ..models.model import db
from ..models.user_vocab_model import UserVocabDB
from ..models.user_model import UserDB

from sqlalchemy import exc
from flask_graphql_auth import (
    get_jwt_identity,
    mutation_jwt_required,
)


class UserVocabMutation(graphene.Mutation):
    """
    INPUT: (uuid, access_token, vocab_id, ...)
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
        uuid = graphene.String(required=True)
        access_token = graphene.String(required=True)
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
        kwargs = parse_kwargs(kwargs)

        auth_db, uuid = check_jwt_with_uuid(kwargs, get_jwt_identity())
        user_vocab_db = UserVocabDB.get_by_uuid_vocab_id(
            uuid=uuid,
            vocab_id=kwargs["vocab_id"],
            with_for_update=True,
            erase_cache=True)
        if user_vocab_db is None:
            user_db = UserDB.get(uuid=uuid)
            if (user_db is None):
                raise InternalServerError(
                    "[Error] for some reason user {} doesn't have user database"
                    .format(kwargs["user_name"] if "user_name" in
                            kwargs else uuid))
            nth_word = user_db.xp

            user_vocab_db = UserVocabDB.add(
                uuid=uuid,
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
                pin_mark=kwargs["pin_mark"] if "pin_mark" in kwargs else None,
                added_mark=kwargs["added_mark"]
                if "added_mark" in kwargs else None)

            try:
                db.session.commit()
            except exc.IntegrityError:
                # user_vocab_db = UserVocabDB.get_by_uuid_vocab_id(
                #     uuid=uuid, vocab_id=kwargs["vocab_id"])
                raise Exception("400|[Warning] user vocab already exists.")

        else:
            filtered_kwargs = {
                k: kwargs[k]
                for k in [
                    "edited_meaning", "book_marked", "question_mark",
                    "star_mark", "pin_mark", "added_mark"
                ] if k in kwargs
            }
            user_vocab_db = UserVocabDB.update(user_vocab_db,
                                               **filtered_kwargs)
        return UserVocabMutation(
            vocab_id=user_vocab_db.vocab_id,
            nth_word=user_vocab_db.nth_word,
            nth_appear=user_vocab_db.nth_appear,
            edited_meaning=user_vocab_db.edited_meaning,
            book_marked=user_vocab_db.book_marked,
            question_mark=user_vocab_db.question_mark,
            star_mark=user_vocab_db.star_mark,
            pin_mark=user_vocab_db.pin_mark,
            added_mark=user_vocab_db.added_mark,
        )
