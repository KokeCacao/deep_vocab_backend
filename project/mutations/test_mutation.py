import graphene
from sqlalchemy import exc

from ..models.model import db
from ..algorithm.vocab_database_creator import BarronDatabaseCreator


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
                print("[SQL Error] " + e.detail)
                return TestMutation(success=False)
            else:
                return TestMutation(success=True)
        elif action == "delete db":
            return TestMutation(success=False)
