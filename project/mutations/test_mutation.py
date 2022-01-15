import graphene
from sqlalchemy import exc

from ..models.model import db
from ..algorithm.vocab_database_creator import BarronDatabaseCreator
from ..utils.util import send_verification
from flask import current_app

class TestMutation(graphene.Mutation):
    """
    mutation {
        test(key: "Koke_Cacao 's secret key", action: "add to db") {
            success
        }
    }
    """
    class Arguments:
        key = graphene.String(required=True)
        action = graphene.String(required=True)

    success = graphene.Boolean()

    @staticmethod
    def mutate(parent, info, **kwargs):
        key = kwargs["key"]
        action = kwargs["action"]

        if key != "Koke_Cacao 's secret key":
            raise Exception("400|Invalid Key")
        if action == "add to db":
            BarronDatabaseCreator().add_barron_to_database()
            try:
                db.session.commit()
            except exc.IntegrityError as e:
                current_app.logger.info("[SQL Error] " + e.detail)
                return TestMutation(success=False)
            else:
                return TestMutation(success=True)
        elif action == "delete users":
            from ..models.auth_model import AuthDB
            from ..models.mark_color_model import MarkColorDB
            from ..models.user_model import UserDB
            from ..models.user_vocab_model import UserVocabDB

            AuthDB.__table__.drop(db.engine)
            MarkColorDB.__table__.drop(db.engine)
            UserDB.__table__.drop(db.engine)
            UserVocabDB.__table__.drop(db.engine)
        elif action == "delete all":
            from ..models.auth_model import AuthDB
            from ..models.mark_color_model import MarkColorDB
            from ..models.user_model import UserDB
            from ..models.user_vocab_model import UserVocabDB
            from ..models.vocab_model import VocabDB

            AuthDB.__table__.drop(db.engine)
            MarkColorDB.__table__.drop(db.engine)
            UserDB.__table__.drop(db.engine)
            UserVocabDB.__table__.drop(db.engine)
            VocabDB.__table__.drop(db.engine)
        elif action == "delete vocab":
            from ..models.vocab_model import VocabDB

            VocabDB.__table__.drop(db.engine)
        elif action == "send email":
            send_verification(to=["su.chen.hanke@gmail.com"],
                              code="000000",
                              debug=True)

        else:
            raise Exception("400|Invalid Action")
        return TestMutation(success=True)
