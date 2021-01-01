import graphene
from .models.model import db
from .models.user_model import User, UserDB
from .models.auth_model import Auth


class Query(graphene.ObjectType):
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
        return "Resolved Hello World! Parent: {}, Info: {}".format(parent, info)

    """
    query {
        user(uuid: "038c4d22-4731-11eb-b378-0242ac130002") {
            uuid
            userName
            avatarUrl
            level
            xp
        }
    }
    """
    # create User field, with required uuid to pass in
    # if required is set to args, then the arg is required
    # if required is set to Field, then all args are required (I'm guessing)
    # you can also use `default_value` if it is not required
    # INPUT: (uuid)
    # OUTPUT: (* | valid uuid), (None | invalid uuid)
    user = graphene.Field(
        User,
        args={
            'uuid': graphene.UUID(required=True),
            #   'public_email': graphene.String(required=False),
            #   'user_name': graphene.String(required=False),
            #   'avatar_url': graphene.String(required=False),
            #   'level': graphene.Int(required=False),
            #   'xp': graphene.Int(required=False),
        })
    @staticmethod
    def resolve_user(parent, info, uuid):
        user_db = UserDB.query.get(str(uuid))
        if (user_db is None): return None
        return User(uuid=user_db.uuid,
                    user_name=user_db.user_name,
                    public_email=user_db.public_email,
                    avatar_url=user_db.avatar_url,
                    level=user_db.level,
                    xp=user_db.xp)


    # INPUT: (username, password), (email, password), (wx_token)
    # DO: login user
    # OUTPUT: (refresh_token, access_token | valid auth), (None | invalid auth)
    auth = graphene.Field(
        Auth,
        args={
            #   'uuid': graphene.UUID(required=True),
            'email': graphene.String(required=False),
            'user_name': graphene.String(required=False),
            'password': graphene.String(required=False),
            #   'access_token': graphene.String(required=False),
            #   'refresh_token': graphene.String(required=False),
            'wx_token': graphene.String(required=False),
        })
    # TODO: implement it
    @staticmethod
    def resolve_auth(parent, info, **kwargs):
        pass