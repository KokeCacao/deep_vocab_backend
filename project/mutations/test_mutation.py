import graphene

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
            db.session.commit()
        elif action == "delete db":
            pass
        return TestMutation(success=True)
