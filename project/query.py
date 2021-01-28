import graphene
from .queries.user_query import UserQuery


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


class Query(graphene.ObjectType, HelloWorldQuery, UserQuery):
    # create User field, with required uuid to pass in
    # if required is set to args, then the arg is required
    # if required is set to Field, then all args are required (I'm guessing)
    # you can also use `default_value` if it is not required
    pass