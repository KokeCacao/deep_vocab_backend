import graphene
from .models.model import db
from .models.user_model import User, UserDB
from .models.auth_model import Auth


class HelloWorldQuery(object):
    """
    query {
        helloWorld
    }
    """
    hello_world = graphene.String()
    # this method resolve the request for `hello_world` variable (which is a string)
    # the first argument is never `self`
    # see https://docs.graphene-python.org/en/latest/types/objecttypes/#resolverimplicitstaticmethod
    @staticmethod
    def resolve_hello_world(parent, info):
        return "Resolved Hello World! Parent: {}, Info: {}".format(
            parent, info)


class UserQuery(object):
    """
    INPUT: ([uuid, user_name], ...)
    DO: fetch database
    OUTPUT: (* | exists in database), (None | doesn't exist in database)

    EXAMPLE INPUT:
    query {
        user(userName: "koke2") {
            uuid
            displayName
            userName
            avatarUrl
            level
            xp
        }
    }
    """
    user = graphene.Field(User,
                          args={
                              'uuid': graphene.UUID(required=False),
                              'user_name': graphene.String(required=False),
                          })

    @staticmethod
    def resolve_user(parent, info, **kwargs):
        def valid_kwargs(kwargs):
            return ("uuid" in kwargs and "user_name" not in kwargs) or (
                "uuid" not in kwargs and "user_name" in kwargs)

        # TODO: make parse_kwargs into a class so that I only have to write once
        def parse_kwargs(kwargs):
            if "uuid" in kwargs:
                kwargs["uuid"] = str(kwargs["uuid"])
                print("[DEBUG] parsed kwargs = {}".format(kwargs))
            return kwargs

        if not valid_kwargs(kwargs):
            raise Exception("400|[Warning] invalid kwargs combinations")
        kwargs = parse_kwargs(kwargs)

        user_db = None
        if "uuid" in kwargs:
            user_db = UserDB.get(kwargs["uuid"])
        elif "user_name" in kwargs:
            user_db = UserDB.get_by_user_name(kwargs["user_name"])

        if (user_db is None):
            raise Exception("400|[Warning] uuid does not exists")
        return User(uuid=user_db.uuid,
                    user_name=user_db.user_name,
                    display_name=user_db.display_name,
                    avatar_url=user_db.avatar_url,
                    level=user_db.level,
                    xp=user_db.xp)


class Query(graphene.ObjectType, HelloWorldQuery, UserQuery):
    # create User field, with required uuid to pass in
    # if required is set to args, then the arg is required
    # if required is set to Field, then all args are required (I'm guessing)
    # you can also use `default_value` if it is not required
    pass