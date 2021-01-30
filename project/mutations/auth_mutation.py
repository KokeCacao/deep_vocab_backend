import graphene

from ..utils.util import parse_kwargs
from ..models.auth_model import AuthDB
from flask_graphql_auth import (
    create_access_token,
    create_refresh_token,
)


# TODO: allow change password / email ect...
# TODO: any field with `$` should be invalid. user name or email with [space] should be invalid
# TODO: allow wx login, see: https://blog.csdn.net/xudailong_blog/article/details/98090158
# or: https://www.jianshu.com/p/e9ab16d52555, https://github.com/OpenFlutter/fluwx
class AuthMutation(graphene.Mutation):
    """
    INPUT: (password, [user_name, email]), (wx_token)
    DO: create access_token, refresh_token if user login with correct credential
    OUTPUT: (access_token, refresh_token | correct credential), (None | incorrect credential)

    EXAMPLE:
    mutation {
        auth(userName: "user3", password: "pass3") {
            uuid
            accessToken
            refreshToken
        }
    }
    """
    class Arguments:
        # if arguments are required by input
        password = graphene.String(required=False)
        user_name = graphene.String(required=False)
        email = graphene.String(required=False)
        wx_token = graphene.String(required=False)

    # if arguments are required to have non-null output
    uuid = graphene.UUID()
    access_token = graphene.String()
    refresh_token = graphene.String()

    @staticmethod
    def mutate(parent, info, **kwargs):
        def valid_kwargs(kwargs):
            # Note: having both user_name and email passed as argument is undefined behavior
            return ("wx_token" in kwargs) or (
                "password" in kwargs and
                ("user_name" in kwargs or "email" in kwargs)) and (
                    ("user_name" in kwargs and "email" not in kwargs) or
                    ("user_name" not in kwargs and "email" in kwargs))

        if not valid_kwargs(kwargs):
            raise Exception("400|[Warning] invalid kwargs combinations.")
        kwargs = parse_kwargs(kwargs)

        # TODO: implement Wechat Login
        if "wx_token" in kwargs:
            raise Exception(
                "400|[Warning] you should not provide wx_token because I have not implement it."
            )

        auth_db = None
        if "user_name" in kwargs:
            auth_db = AuthDB.get_by_user_name(kwargs["user_name"])
        if "email" in kwargs: auth_db = AuthDB.get_by_email(kwargs["email"])

        if (auth_db is None):
            raise Exception("400|[Warning] no such user in database.")

        if kwargs["password"] != auth_db.password:
            raise Exception("400|[Warning] invalid password.")

        # TODO: log user out if changed something important
        return AuthMutation(
            uuid=auth_db.uuid,
            access_token=create_access_token(identity=auth_db.uuid),
            refresh_token=create_refresh_token(identity=auth_db.uuid))