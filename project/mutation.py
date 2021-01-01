import graphene
from .models.model import db
from .models.user_model import User, UserDB
from .models.auth_model import Auth
"""
mutation {
    auth(password: "hji", userName: "user") {
        accessToken
        refreshToken
    }
}

"""


class AuthMutation(graphene.Mutation):
    # if requred in non-null return
    access_token = graphene.String(required=True)
    refresh_token = graphene.String(required=True)

    class Arguments:
        # if required by input
        user_name = graphene.String(required=True)
        password = graphene.String(required=True)

    @staticmethod
    def mutate(parent, info, **kwargs):
        # user = User.query.filter_by(user_name=kwargs["user_name"],password=password).first()
        # print(user)
        # if not user:
        #     raise Exception('Authenication Failure : User is not registered')
        return AuthMutation(access_token=kwargs["user_name"],
                            refresh_token=kwargs["user_name"])


class UserMutation(graphene.Mutation):
    user = graphene.Field(User)

    class Arguments:
        uuid = graphene.String(required=True)
        public_email = graphene.String(required=False)
        user_name = graphene.String(required=False)
        avatar_url = graphene.String(required=False)
        level = graphene.Int(required=False)
        xp = graphene.Int(required=False)

    def mutate():
        pass


# ...: means input with selection from all other variables
# |: follow by condition
# []: means input with selection of one from variables within
# *: means output all fields
# -: means cannot input this argument, or not included
class Mutation(graphene.ObjectType):
    """
    mutation {
        user(uuid: "038c4d22-4731-11eb-b378-0242ac130002", userName: "Koke_Cacao", xp: 1, accessToken: "token") {
            uuid
            userName
            avatarUrl
        }
    }
    """
    # INPUT: (uuid, access_token, ...)
    # DO: update user profile with input arguments if access_token in database
    # OUTPUT: (* | access_token in database), (None | access_token in database)
    user = graphene.Field(User,
                          args={
                              'uuid': graphene.UUID(required=True),
                              'access_token': graphene.String(required=True),
                              'public_email': graphene.String(required=False),
                              'user_name': graphene.String(required=False),
                              'avatar_url': graphene.String(required=False),
                              'level': graphene.Int(required=False),
                              'xp': graphene.Int(required=False),
                          })
    # must match the same as above
    @staticmethod
    def resolve_user(parent, info, **kwargs):
        kwargs = User.parse_kwargs(**kwargs)
        # TODO: check if access_token in database
        user_db = UserDB.get(kwargs['uuid'])

        if (user_db is None):
            user_db = UserDB.add(**kwargs)
        else:
            user_db = UserDB.update(user_db, **kwargs)

        db.session.commit()
        return user_db.to_graphql_object()

    # INPUT: (access_token, ..., -refresh_token)
    # DO: if valid access_token: change ... accordingly
    # OUTPUT: (* | valid access_token), (None | invalid access_token)
    auth = graphene.Field(
        Auth,
        args={
            'uuid': graphene.UUID(required=True),
            'email': graphene.String(required=False),
            'user_name': graphene.String(required=False),
            'password': graphene.String(required=False),
            'access_token': graphene.String(required=False),
            #   'refresh_token': graphene.String(required=False),
            'wx_token': graphene.String(required=False),
        })

    # TODO: write me
    def resolve_auth(parent, info, **kwargs):
        pass

    auth = AuthMutation.Field()