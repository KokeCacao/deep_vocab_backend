import graphene
import uuid as UUID

from ..models.auth_model import AuthDB
from ..utils.util import parse_kwargs
from ..models.model import db
from ..models.user_model import UserDB
from flask_graphql_auth import (
    create_access_token,
    create_refresh_token,
)


# TODO: email verification on user create account
# For JWT library, see: https://medium.com/python-in-plain-english/flask-graphql-jwt-authentication-204c78adb312
# or see: https://github.com/NovemberOscar/Flask-GraphQL-Auth/blob/master/examples/basic.py#L24
class CreateUserMutation(graphene.Mutation):
    """
    INPUT: (user_name, password, email)
    DO: create user if user_name and email is unique
    OUTPUT: (None | user_name or email already exists), (access_token, refresh_token, uuid | else)

    EXAMPLE:
    mutation {
        createUser(userName: "user3", password: "pass3", email: "3hanke.chen@ssfs.org") {
            uuid
            accessToken
            refreshToken
        }
    }
    """
    class Arguments:
        user_name = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    uuid = graphene.UUID()
    access_token = graphene.String()
    refresh_token = graphene.String()

    @staticmethod
    def mutate(parent, info, **kwargs):
        def valid_kwargs(kwargs):
            return "user_name" in kwargs and "password" in kwargs and "email" in kwargs

        if not valid_kwargs(kwargs):
            raise Exception("400|[Warning] invalid kwargs combinations")
        kwargs = parse_kwargs(kwargs)

        uuid = str(UUID.uuid4())
        try:
            AuthDB.add(uuid=uuid,
                       email=kwargs["email"],
                       user_name=kwargs["user_name"],
                       password=kwargs["password"],
                       access_token=None,
                       refresh_token=None,
                       wx_token=None)
            UserDB.add(uuid=uuid,
                       user_name=kwargs["user_name"],
                       display_name=None,
                       avatar_url=None,
                       level=0,
                       xp=0)
            db.session.commit()
        except:
            raise Exception("400|[Warning] user_name or email already exists")

        return CreateUserMutation(uuid=uuid,
                                  access_token=create_access_token(uuid),
                                  refresh_token=create_refresh_token(uuid))