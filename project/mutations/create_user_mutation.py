import graphene
import uuid as UUID

from ..models.auth_model import AuthDB
from ..utils.util import parse_kwargs, sha256_six_int, send_verification
from ..models.model import db
from ..models.user_model import UserDB

from datetime import datetime
from sqlalchemy import exc
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
        createUser(userName: "user3", password: "pass3", email: "hankec@andrew.cmu.edu") {
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
        email_verification = graphene.String(required=False)

    uuid = graphene.UUID()
    access_token = graphene.String()
    refresh_token = graphene.String()

    @staticmethod
    def mutate(parent, info, **kwargs):
        kwargs = parse_kwargs(kwargs)

        if ("email_verification" in kwargs):
            # check for verification code
            email_verification = kwargs["email_verification"]

            time = datetime.utcnow().timestamp()  # float where int part is sec
            time = int(time)
            time = int(time / 60 / 10)  # floor division by 10 minutes
            time2 = time + 1

            code = sha256_six_int("code={}/{}/{};time={}".format(
                kwargs["email"], kwargs["user_name"], kwargs["password"],
                time))
            code2 = sha256_six_int("code={}/{}/{};time={}".format(
                kwargs["email"], kwargs["user_name"], kwargs["password"],
                time2))

            if (email_verification != code and email_verification != code2):
                raise Exception(
                    "400|[Warning] invalid email verification code.")

            # verification code is good!
            uuid = str(UUID.uuid4())
            AuthDB.add(
                uuid=uuid,
                email=kwargs["email"],
                user_name=kwargs["user_name"],
                password=kwargs["password"],
            )
            UserDB.add(
                uuid=uuid,
                user_name=kwargs["user_name"],
            )

            try:
                db.session.commit()
            except exc.IntegrityError:
                raise Exception(
                    "400|[Warning] user_name or email already exists.")

            return CreateUserMutation(uuid=uuid,
                                      access_token=create_access_token(uuid),
                                      refresh_token=create_refresh_token(uuid))
        else:
            if AuthDB.get_by_email(kwargs["email"]) != None:
                raise Exception("400|[Warning] email already exists.")
            if AuthDB.get_by_user_name(kwargs["user_name"]) != None:
                raise Exception("400|[Warning] user_name already exists.")

            to = kwargs["email"]

            time = datetime.utcnow().timestamp()  # float where int part is sec
            time = int(time)
            time = int(time / 60 / 10)  # floor division by 10 minutes

            code = sha256_six_int("code={}/{}/{};time={}".format(
                kwargs["email"], kwargs["user_name"], kwargs["password"],
                time))
            print("send code = {}; time = {}".format(code, time))
            send_verification(to=[to], code=code)
            return CreateUserMutation(uuid=None,
                                      access_token=None,
                                      refresh_token=None)
