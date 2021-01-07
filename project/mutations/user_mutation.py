import graphene

from werkzeug.exceptions import InternalServerError
from ..utils.util import parse_kwargs
from ..models.model import db
from ..models.user_model import UserDB
from flask_graphql_auth import (
    get_jwt_identity,
    mutation_jwt_required,
)


class UserMutation(graphene.Mutation):
    """
    INPUT: ([uuid, user_name], access_token, ...)
    DO: update user profile with input arguments if access_token in database
    OUTPUT: (* | access_token in database), (None | access_token in database)

    EXAMPLE INPUT:
    mutation {
        user(uuid: "2d480cd1-7e8b-4040-a81e-76191e4da0e5", displayName: "display", accessToken: "token") {
            displayName
            avatarUrl
            level
            xp
        }
    }
    """
    class Arguments:
        uuid = graphene.String(required=False)
        access_token = graphene.String(required=True)
        user_name = graphene.String(required=False)
        display_name = graphene.String(required=False)
        avatar_url = graphene.String(required=False)

    # These are objects I can request
    display_name = graphene.String()
    avatar_url = graphene.String()
    level = graphene.Int()
    xp = graphene.Int()

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

        # TODO: check if access_token in database
        user_db = None
        if "uuid" in kwargs:
            if (get_jwt_identity() != kwargs["uuid"]):
                raise Exception("400|[Warning] incorrect uuid")
            user_db = UserDB.get(kwargs["uuid"])
        elif "user_name" in kwargs:
            user_db = UserDB.get_by_user_name(kwargs["user_name"])
            if (get_jwt_identity() != user_db.uuid):
                raise Exception("400|[Warning] incorrect uuid")

        if (user_db is None):
            raise InternalServerError(
                "[Error] for some reason user {} doesn't have user database".
                format(kwargs["user_name"] if "user_name" in
                       kwargs else kwargs["uuid"]))
        else:
            user_db = UserDB.update(
                user_db,
                display_name=kwargs["display_name"]
                if "display_name" in kwargs else None,
                avatar_url=kwargs["avatar_url"]
                if "avatar_url" in kwargs else None,
            )

        db.session.commit()
        return user_db.to_graphql_object()