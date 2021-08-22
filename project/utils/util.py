import hashlib

from werkzeug.exceptions import InternalServerError
from ..models.auth_model import AuthDB


def parse_kwargs(kwargs):
    if "uuid" in kwargs:
        kwargs["uuid"] = str(kwargs["uuid"])
        # print("[DEBUG] parsed uuid = {}".format(kwargs))
    if "password" in kwargs:
        salt = "いつもひとりで歩いてた;振り返るとみんなは遠くそれでもあたしは歩いた;それが強さだったもう何も恐くない;そう呟いてみせるいつか人は一人になって;思い出の中に生きてくだけ孤独さえ愛し笑ってられるように;あたしは戦うんだ涙なんて見せないんだいつもひとりで歩いてた;行く先には崖が待ってたそれでもあたしは歩いた;強さの証明のため吹きつける強い風;汗でシャツが張り付くいつか忘れてしまえるなら;生きることそれはたやすいもの忘却の彼方へと落ちていくなら;それは逃げることだろう生きた意味すら消えるだろう風はやがて凪いでた;汗も乾いてお腹が空いてきたな;何かあったっけ賑やかな声と共にいい匂いがやってきたいつもひとりで歩いてた;みんなが待っていたいつか人は一人になって;思い出の中に生きてくだけそれでもいい;安らかなこの気持ちは;それを仲間と呼ぶんだいつかみんなと過ごした日々も忘れてどこかで生きてるよその時はもう強くなんかないよ普通の女の子の弱さで涙を零すよ"
        kwargs["password"] = hashlib.sha256(
            (kwargs["password"] + salt).encode("utf-8")).hexdigest()
        # print("[DEBUG] parsed password = {}".format(kwargs))
    return kwargs


def check_jwt_with_uuid(kwargs, jwt_identity):
    assert "uuid" in kwargs
    if "jwt_error" in kwargs: raise Exception("401|[Warning] JWT incorrect.")
    if jwt_identity != kwargs["uuid"]:
        raise Exception("400|[Warning] incorrect uuid.")

    auth_db = AuthDB.get(kwargs["uuid"])

    if auth_db is None:
        raise InternalServerError(
            "for some reason user {} doesn't have auth database.".format(
                kwargs["uuid"]))
    return auth_db, kwargs["uuid"]