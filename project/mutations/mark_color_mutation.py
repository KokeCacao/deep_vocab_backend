from datetime import datetime, timedelta
import graphene
import math

from ..utils.util import parse_kwargs, check_jwt_with_uuid
from ..models.model import db, ColorModel
from ..models.mark_color_model import MarkColorDB
from ..models.user_vocab_model import UserVocabDB

from sqlalchemy import exc
from flask_graphql_auth import (
    get_jwt_identity,
    mutation_jwt_required,
)


class MarkColorMutation(graphene.Mutation):
    """
    INPUT: (uuid, access_token, vocab_id, index, color, time)
    DO: add or update mark_color if access_token in database
    OUTPUT: (* | access_token in database), (None | access_token in database)

    EXAMPLE INPUT:
    mutation {
        markColor(uuid: "2d480cd1-7e8b-4040-a81e-76191e4da0e5", accessToken: "token", vocabId: "id", index: 0, color: black, time: "2021-01-23T02:26:15.196092") {
            index
            color
            time
        }
    }
    """
    # graphene.Enum.from_enum(ColorModel) can't be used twice without storing the value
    # See: https://github.com/graphql-python/graphene-sqlalchemy/issues/211
    from functools import lru_cache
    graphene.Enum.from_enum = lru_cache(maxsize=None)(graphene.Enum.from_enum)

    class Arguments:
        uuid = graphene.String(required=True)
        access_token = graphene.String(required=True)
        vocab_id = graphene.String(required=True)
        index = graphene.Int(required=True)
        color = graphene.Enum.from_enum(ColorModel)(required=True)
        time = graphene.DateTime(required=True)

    vocab_id = graphene.String()
    index = graphene.Int()
    color = graphene.Enum.from_enum(ColorModel)()
    time = graphene.DateTime()

    @staticmethod
    @mutation_jwt_required
    def mutate(parent, info, **kwargs):
        kwargs = parse_kwargs(kwargs)
        auth_db, uuid = check_jwt_with_uuid(kwargs, get_jwt_identity())

        index = kwargs["index"]
        # make sure index is >= 0
        if index < 0: raise Exception("400|[Warning] index < 0")

        # make sure index-1 already exist in database or index=0
        last_mark_color_db = MarkColorDB.get_by_uuid_vocab_id_index(
            uuid, kwargs["vocab_id"], index - 1)
        if index != 0 and last_mark_color_db == None:
            raise Exception("400|[Warning] index-1 does not exist in database")

        # if index already exist in database, edit such entry, return such entry
        # TODO: if index already exist in database, delete entries after it
        mark_color_db = MarkColorDB.get_by_uuid_vocab_id_index(
            uuid,
            kwargs["vocab_id"],
            index,
            with_for_update=True,
            erase_cache=True)
        if mark_color_db != None:
            mark_color_db = MarkColorDB.update(mark_color_db,
                                               color=kwargs["color"],
                                               time=kwargs["time"])
        else:
            # else create new entry
            mark_color_db = MarkColorDB.add(
                uuid=uuid,
                vocab_id=kwargs["vocab_id"],
                index=kwargs["index"],
                color=kwargs["color"],
                time=kwargs["time"])  # TODO: use server time instead?

        # add UserVocabDB when needed
        # add nth_word, calculate refresh time
        user_vocab_db = UserVocabDB.get_by_uuid_vocab_id(uuid,
                                                         kwargs["vocab_id"],
                                                         with_for_update=True,
                                                         erase_cache=True)
        if user_vocab_db is None:
            raise Exception("400|[Warning] vocab not added to UserVocabDB.")
        else:
            user_vocab_db = UserVocabDB.update(
                user_vocab_db, nth_word=user_vocab_db.nth_word + 1)

        # calculate the time when this vocab should appear in task bar
        def get_LTM_and_refresh_time(user_vocab_db, color, last_mark_color_db):
            """
            This function does two things:
            1. return the refresh time (next time in which user should recieve new push notification) by 50% sort term memory
            2. update internal long term memory in database

            y = l+\left(100-l\right)\cdot e^{\frac{-x}{s}}
            s = calculated by MarkColor
            l = LTM stored in vocab
            best time when y = 50
            """
            # Settings of Constants
            desired_short_term_mem = 50.0  # could be variable
            mem_max = 100.0  # constant

            # calculate memory stability based on mark color
            """
            Actual Refresh Time upon first remember:
                block: 30s
                red: 3min
                yellow: 17min
                green: 80min
            """
            switch = {
                "black": 60.0,  # 60s will <50% if no LTM, 4min if 50% LTM
                "red":
                5.0 * 60.0,  # 5min will <50% if no LTM, 58min if 50% LTM
                "yellow":
                25.0 * 60.0,  # 25min will <50% if no LTM, 83min if 50% LTM
                "green":
                125.0 * 60.0,  # 2h will <50% if no LTM, 2.41h if 50% LTM
            }
            mem_stability = switch[color]

            time_diff = 0.0 if last_mark_color_db == None else (
                datetime.utcnow() - last_mark_color_db.time).total_seconds()
            long_term_mem_lost_by_time = 0.005 * time_diff
            print("Your long_term_mem_lost_by_time is {}".format(
                long_term_mem_lost_by_time))

            # update long_term_mem by subtracting lost due to time before use it to calculate more
            long_term_mem = user_vocab_db.long_term_mem - long_term_mem_lost_by_time
            print("Your long_term_mem before look at this vocab is {}".format(
                long_term_mem))

            # calculate short_term_mem before user look at the vocab
            # The 60s here is added to prevent short_tem_mem = 100 upon first remember
            short_term_mem_tmp = (mem_max - long_term_mem) * math.exp(
                -(60.0 + time_diff) / mem_stability)
            short_term_mem = long_term_mem + short_term_mem_tmp
            print("Your short_term_mem is {}".format(short_term_mem))

            # now that the user looked at the vocab, update user's new long_term_mem
            # (mem_max - short_term_mem): as our short term memory decrease, the better we memorize
            # (2*long_term_mem_lost_by_time): but after a long long time, our memory basically start again, and long_term_mem should decrease
            long_term_mem = long_term_mem + (
                mem_max - short_term_mem) / 16 - long_term_mem_lost_by_time
            print("Your new long_term_mem is {}".format(long_term_mem))
            if (long_term_mem < 0):
                long_term_mem = 0
                print("You have fully forgot this vocab.")

            # although mem_stability is not relevent, we use it as a predictor of the curve
            if desired_short_term_mem > long_term_mem:
                # approximation of formula above
                refresh_time_diff = -mem_stability * math.log(
                    (desired_short_term_mem - long_term_mem) /
                    (mem_max - long_term_mem))
                assert refresh_time_diff > 0
            else:
                refresh_time_diff = 300.0  # constant, will approximate later. Represent how often should remind after LTM > 50%

            refresh_time = datetime.utcnow() + timedelta(
                0, refresh_time_diff)  # days, seconds, then other fields.
            print("We will update after {} seconds ({})".format(
                refresh_time_diff, refresh_time.isoformat()))

            return long_term_mem, refresh_time

        long_term_mem, refresh_time = get_LTM_and_refresh_time(
            user_vocab_db, kwargs["color"], last_mark_color_db)
        UserVocabDB.update(user_vocab_db,
                           long_term_mem=long_term_mem,
                           refresh_time=refresh_time)

        try:
            db.session.commit()
        except exc.IntegrityError:
            raise Exception(
                "400|[Warning] Unique constraints failed due to concurrency in uuid_vocab_id_index."
            )

        return MarkColorMutation(
            vocab_id=mark_color_db.vocab_id,
            index=mark_color_db.index,
            color=mark_color_db.color,
            time=mark_color_db.time,
        )
