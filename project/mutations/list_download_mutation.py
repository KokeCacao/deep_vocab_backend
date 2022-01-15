import graphene

from datetime import datetime
from ..utils.util import parse_kwargs, check_jwt_with_uuid
from ..models.user_vocab_model import UserVocabDB
from ..models.vocab_model import VocabDB
from ..models.mark_color_model import MarkColorDB
from ..models.model import VocabListHeader, VocabUserVocab
from ..algorithm.vocab_database_creator import BarronDatabaseCreator
from flask_graphql_auth import (
    get_jwt_identity,
    mutation_jwt_required,
)
from flask import current_app


class ListDownloadMutation(graphene.Mutation):
    """
    INPUT: (uuid, access_token, list_id, ...)
    DO: get all vocab from list_id
    OUTPUT: (vocabs | access_token in database), (None | access_token in database)

    EXAMPLE INPUT:
    mutation {
        listDownload(uuid: "uuid", accessToken: "token", listId: 0) {
         vocabs
        }
    }
    """
    class Arguments:
        uuid = graphene.String(required=True)
        access_token = graphene.String(required=True)
        list_id = graphene.Int(required=True)

    header = graphene.Field(VocabListHeader)
    vocabs = graphene.List(VocabUserVocab)

    @staticmethod
    @mutation_jwt_required
    def mutate(parent, info, **kwargs):
        kwargs = parse_kwargs(kwargs)
        auth_db, uuid = check_jwt_with_uuid(kwargs, get_jwt_identity())

        list_header = dict()
        # list_header = {
        #     0: {
        #         "name": "list_name",
        #         "list_id": 0,
        #         "edition":
        #         datetime.fromisoformat("2021-01-23T02:26:15.196899"),
        #         "vocab_ids":
        #         set(str(vocab_int) for vocab_int in range(1, 100))
        #     },
        #     1: {
        #         "name": "list_name",
        #         "list_id": 1,
        #         "edition":
        #         datetime.fromisoformat("2017-01-01T12:30:59.000000"),
        #         "vocab_ids": {"vocab_id", "0"}
        #     },
        # }
        barron_database_creator = BarronDatabaseCreator()
        list_id, list_header = barron_database_creator.get_header()
        list_header[list_id] = list_header

        header_data = list_header.get(kwargs["list_id"])

        # get vocab data
        vocab_dbs = VocabDB.gets(header_data.get("vocab_ids", {}), sorted=True)
        vocab_ids = [vocab_db.vocab_id for vocab_db in vocab_dbs]

        # get user vocab data
        user_vocab_dbs = (UserVocabDB.get_by_uuid_vocab_id(uuid, vocab_id)
                          for vocab_id in vocab_ids)

        # get mark_colo_dict as dictionary of vocab_id and markcolor list
        mark_color_dict = MarkColorDB.get_by_uuid_to_vocab_id_dict(uuid)
        mark_colorses = (mark_color_dict.get(vocab_id, [])
                         for vocab_id in vocab_ids)


        current_app.logger.info("[ListDownloadedMutation] Combing Vocab and UserVocab")

        # combine them
        combined = (VocabUserVocab().from_vocab_and_user_vocab(
            vocab=vocab_db,
            user_vocab=user_vocab_db,
            mark_colors_list=mark_colors)
                    for vocab_db, user_vocab_db, mark_colors in zip(
                        vocab_dbs, user_vocab_dbs, mark_colorses))
        
        current_app.logger.info("[ListDownloadedMutation] Returning the data")
        return ListDownloadMutation(header=VocabListHeader(
            name=header_data.get("name"),
            list_id=header_data.get("list_id"),
            edition=header_data.get("edition"),
            vocab_ids=header_data.get("vocab_ids")),
                                    vocabs=list(combined))
