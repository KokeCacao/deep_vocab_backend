import graphene
from ..utils.util import parse_kwargs
from ..models.user_model import UserDB


# TODO: standarlize query like what we do on mutation
class User(graphene.ObjectType):
    # if resolver not specified, use default resolver
    # see https://docs.graphene-python.org/en/latest/types/objecttypes/#defaultresolver
    uuid = graphene.UUID()
    display_name = graphene.String()
    user_name = graphene.String()
    avatar_url = graphene.String()
    level = graphene.Int()
    xp = graphene.Int()


class UserQuery(object):
    """
    INPUT: ([uuid, user_name], ...)
    DO: fetch database
    OUTPUT: (* | exists in database), (None | doesn't exist in database)

    EXAMPLE INPUT:
    query {
        user(userName: "user3") {
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