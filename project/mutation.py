import graphene

from .models.auth_model import Auth
from .mutations.test_mutation import TestMutation
from .mutations.auth_mutation import AuthMutation
from .mutations.user_mutation import UserMutation
from .mutations.refresh_mutation import RefreshMutation
from .mutations.create_user_mutation import CreateUserMutation
from .mutations.mark_color_mutation import MarkColorMutation
from .mutations.user_vocab_mutation import UserVocabMutation
from .mutations.refresh_vocabs_mutation import RefreshVocabMutation


# ...: means input with selection from all other variables
# |: follow by condition
# []: means input with selection of one from variables within
# *: means output all fields
# -: means cannot input this argument, or not included
class Mutation(graphene.ObjectType):
    # TODO: standarlize and document database models
    # Flask will only create table when such import of DB is under one of mutation
    test = TestMutation.Field()
    auth = AuthMutation.Field()
    user = UserMutation.Field()
    refresh = RefreshMutation.Field()
    create_user = CreateUserMutation.Field()
    mark_color = MarkColorMutation.Field()
    user_vocab = UserVocabMutation.Field()
    refresh_vocab = RefreshVocabMutation.Field()