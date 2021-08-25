import graphene
from datetime import datetime

from ..utils.util import parse_kwargs


class Update(graphene.ObjectType):
    latest_version = graphene.String()
    latest_build_number = graphene.Int()
    latest_date = graphene.DateTime()
    change_logs = graphene.List(graphene.String)
    should_update = graphene.Boolean()
    breaking = graphene.Boolean()


class UpdateQuery(object):
    """
    INPUT: ([version, build_number], ...)
    DO: check for update
    OUTPUT: (*)

    EXAMPLE INPUT:
    query {
        update(version: "v0.0.0", buildNumber: 1) {
            latestVersion
            latestBuildNumber
            latestDate
            changeLogs
            shouldUpdate
            breaking
        }
    }
    """
    update = graphene.Field(Update,
                            args={
                                "version": graphene.String(),
                                "build_number": graphene.Int(),
                            })

    @staticmethod
    def resolve_update(parent, info, **kwargs):
        kwargs = parse_kwargs(kwargs)

        version = kwargs["version"]
        build_number = kwargs["build_number"]

        return Update(latest_version="0.1.0",
                      latest_build_number=0,
                      latest_date=datetime.utcnow(),
                      change_logs=[""],
                      should_update=True,
                      breaking=False)
