import graphene

from .models.auth_model import Auth
from .mutations.auth_mutation import AuthMutation
from .mutations.user_mutation import UserMutation
from .mutations.refresh_mutation import RefreshMutation
from .mutations.create_user_mutation import CreateUserMutation


# ...: means input with selection from all other variables
# |: follow by condition
# []: means input with selection of one from variables within
# *: means output all fields
# -: means cannot input this argument, or not included
class Mutation(graphene.ObjectType):
    # INPUT: (access_token, ..., -refresh_token)
    # DO: if valid access_token: change ... accordingly
    # OUTPUT: (* | valid access_token), (None | invalid access_token)
    # TODO: remove deprecate
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

    # TODO: standarlize and document database models

    auth = AuthMutation.Field()
    user = UserMutation.Field()
    refresh = RefreshMutation.Field()
    create_user = CreateUserMutation.Field()