import graphene
import uuid as UUID

from werkzeug.exceptions import InternalServerError

from ..models.auth_model import AuthDB
from ..utils.util import parse_kwargs, sha256_six_int, send_verification, send_change_password
from ..models.model import db
from ..models.user_model import UserDB

from datetime import datetime
from sqlalchemy import exc
from flask_graphql_auth import (
    create_access_token,
    create_refresh_token,
)
from flask import current_app


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
        user_name = graphene.String(required=False)
        password = graphene.String(required=False)
        email = graphene.String(required=False)
        email_verification = graphene.String(required=False)

    uuid = graphene.UUID()
    access_token = graphene.String()
    refresh_token = graphene.String()

    @staticmethod
    def mutate(parent, info, **kwargs):
        kwargs = parse_kwargs(kwargs)

        # create user given email verification
        if ("email_verification" in kwargs and "user_name" in kwargs
                and "email" in kwargs and "password" in kwargs):
            # check for verification code
            email_verification = kwargs["email_verification"]

            # TODO: time should be longer, it does not seem by 10 min
            time = datetime.utcnow().timestamp()  # float where int part is sec
            time = int(time)
            time = int(time / 60 / 10)  # floor division by 10 minutes
            time2 = time + 1

            code = sha256_six_int("create={}/{}/{};time={}".format(
                kwargs["email"], kwargs["user_name"], kwargs["password"],
                time))
            code2 = sha256_six_int("create={}/{}/{};time={}".format(
                kwargs["email"], kwargs["user_name"], kwargs["password"],
                time2))

            if (email_verification != code and email_verification != code2):
                current_app.logger.info("email_verification {} is not {} or {}".format(email_verification, code, code2))
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

        # request email verification when registration
        elif ("email_verification" not in kwargs and "user_name" in kwargs
              and "email" in kwargs and "password" in kwargs):
            if AuthDB.get_by_email(kwargs["email"]) != None:
                raise Exception("400|[Warning] email already exists.")

            if AuthDB.get_by_user_name(kwargs["user_name"]) != None:
                raise Exception("400|[Warning] user_name already exists.")

            to = kwargs["email"]

            time = datetime.utcnow().timestamp()  # float where int part is sec
            time = int(time)
            time = int(time / 60 / 10)  # floor division by 10 minutes

            code = sha256_six_int("create={}/{}/{};time={}".format(
                kwargs["email"], kwargs["user_name"], kwargs["password"],
                time))
            
            current_app.logger.info("send create code = {}; time = {}".format(code, time))
            send_verification(to=[to], code=code)
            return CreateUserMutation(uuid=None,
                                      access_token=None,
                                      refresh_token=None)

        # request email verification when recover password
        elif ("email_verification" not in kwargs and "user_name" not in kwargs
              and "email" in kwargs and "password" not in kwargs):
            auth_db = AuthDB.get_by_email(kwargs["email"])
            if auth_db != None:
                # old password ensure user cannot change password again
                # using the same code
                old_password = auth_db.password

                # if kwargs["user_name"] is empty
                # perhaps you want to change password
                to = kwargs["email"]

                time = datetime.utcnow().timestamp(
                )  # float where int part is sec
                time = int(time)
                time = int(time / 60 / 10)  # floor division by 10 minutes

                code = sha256_six_int("recover={}/{};time={}".format(
                    kwargs["email"], old_password, time))

                current_app.logger.info("send change code = {}; time = {}".format(code, time))
                send_change_password(to=[to], code=code, debug=True)
                return CreateUserMutation(uuid=None,
                                          access_token=None,
                                          refresh_token=None)
            else:
                raise Exception("400|[Warning] user does not exists.")

        # give feedback on verification code while recovering
        elif ("email_verification" in kwargs and "user_name" not in kwargs
              and "email" in kwargs and "password" not in kwargs):
            # check for verification code
            auth_db = AuthDB.get_by_email(kwargs["email"])
            old_password = auth_db.password

            email_verification = kwargs["email_verification"]

            time = datetime.utcnow().timestamp()  # float where int part is sec
            time = int(time)
            time = int(time / 60 / 10)  # floor division by 10 minutes
            time2 = time + 1

            code = sha256_six_int("recover={}/{};time={}".format(
                kwargs["email"], old_password, time))
            code2 = sha256_six_int("recover={}/{};time={}".format(
                kwargs["email"], old_password, time2))

            if (email_verification != code and email_verification != code2):
                raise Exception(
                    "400|[Warning] invalid email verification code.")

            return CreateUserMutation(uuid=None,
                                      access_token=None,
                                      refresh_token=None)

        # finishing up recover
        elif ("email_verification" in kwargs and "user_name" not in kwargs
              and "email" in kwargs and "password" in kwargs):
            # check for verification code
            auth_db = AuthDB.get_by_email(kwargs["email"],
                                          with_for_update=True)
            old_password = auth_db.password

            email_verification = kwargs["email_verification"]

            time = datetime.utcnow().timestamp()  # float where int part is sec
            time = int(time)
            time = int(time / 60 / 10)  # floor division by 10 minutes
            time2 = time + 1

            code = sha256_six_int("recover={}/{};time={}".format(
                kwargs["email"], old_password, time))
            code2 = sha256_six_int("recover={}/{};time={}".format(
                kwargs["email"], old_password, time2))

            if (email_verification != code and email_verification != code2):
                raise Exception(
                    "400|[Warning] invalid email verification code.")

            # verification code is good!
            AuthDB.update(auth_db, password=kwargs["password"])

            try:
                db.session.commit()
            except exc.IntegrityError:
                raise InternalServerError(
                    "[CreateUserMutation] change password failed")

            return CreateUserMutation(
                uuid=auth_db.uuid,
                access_token=create_access_token(auth_db.uuid),
                refresh_token=create_refresh_token(auth_db.uuid))
        else:
            raise Exception("400|[Warning] invalid request.")
