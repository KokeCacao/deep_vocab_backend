import graphene

from ..utils.util import parse_kwargs, check_jwt_with_uuid
from flask_graphql_auth import (
    get_jwt_identity,
    create_access_token,
    mutation_jwt_refresh_token_required,
)


class RefreshMutation(graphene.Mutation):
    # TODO: also check if the user has expired access_token
    """
    INPUT: (uuid, refresh_token), (uuid, refresh_token, access_token)
    DO: create access_token, if user gives correct refresh_token correspond to uuid
    OUTPUT: (access_token, refresh_token | correct refresh_token with uuid), (None | incorrect refresh_token with uuid)

    EXAMPLE INPUT:
    mutation {
        refresh(uuid: "3f4a98c7-e622-455a-adb2-10bce8b4a298", refreshToken: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTYwOTc1MzIwNSwibmJmIjoxNjA5NzUzMjA1LCJqdGkiOiI1YzBlYTc0YS1lMjRkLTQ0NjAtOTE1YS1mOWI5MmRiYzhkMDYiLCJpZGVudGl0eSI6IjNmNGE5OGM3LWU2MjItNDU1YS1hZGIyLTEwYmNlOGI0YTI5OCIsImV4cCI6MTYxMjM0NTIwNX0.930zVW5e7oDkxQ8GNVpHVqy8aBGE0e5oN4CN7BG1Sl0") {
            accessToken
            refreshToken
        }
    }
    """
    class Arguments:
        uuid = graphene.UUID(required=True)
        access_token = graphene.String(required=False)
        refresh_token = graphene.String(required=True)

    access_token = graphene.String()
    refresh_token = graphene.String()

    @staticmethod
    @mutation_jwt_refresh_token_required
    def mutate(parent, info, **kwargs):
        kwargs = parse_kwargs(kwargs)
        auth_db, uuid = check_jwt_with_uuid(kwargs, get_jwt_identity())

        return RefreshMutation(access_token=create_access_token(identity=uuid),
                               refresh_token=kwargs["refresh_token"])