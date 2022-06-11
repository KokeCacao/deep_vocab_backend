import graphene

from ..utils.util import parse_kwargs, check_jwt_with_uuid
from database import db
from ..models.user_model import UserDB
from werkzeug.exceptions import InternalServerError
from flask_graphql_auth import (
    get_jwt_identity,
    mutation_jwt_required,
)


class UserMutation(graphene.Mutation):
    """
    INPUT: (uuid, access_token, ...)
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
        uuid = graphene.String(required=True)
        access_token = graphene.String(required=True)
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
        kwargs = parse_kwargs(kwargs)

        auth_db, uuid = check_jwt_with_uuid(kwargs, get_jwt_identity())

        # TODO: check if access_token in database
        user_db = UserDB.get(uuid, with_for_update=True, erase_cache=True)
        if user_db is None:
            raise InternalServerError(
                "for some reason user {} doesn't have auth database.".format(
                    kwargs["uuid"]))

        user_db = UserDB.update(
            user_db,
            display_name=kwargs["display_name"]
            if "display_name" in kwargs else None,
            avatar_url=kwargs["avatar_url"]
            if "avatar_url" in kwargs else None,
        )

        db.session.commit()
        return UserMutation(
            uuid=user_db.uuid,
            access_token=user_db.access_token,
            display_name=user_db.display_name,
            avatar_url=user_db.display_name,
        )