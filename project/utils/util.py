import hashlib
import smtplib
import email
import os
# simple email message
from email.message import EmailMessage
# Optional _subtype defaults to mixed, but can be used to specify the subtype of the message.
# A Content-Type header of multipart/_subtype will be added to the message object.
# A MIME-Version header will also be added
from email.mime.multipart import MIMEMultipart
# no attachment
from email.mime.text import MIMEText

from werkzeug.exceptions import InternalServerError
from ..models.auth_model import AuthDB


def parse_kwargs(kwargs):
    for key in list(kwargs.keys()):
        if str(kwargs[key]) == "":
            del kwargs[key]
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


def sha256(string):
    return hashlib.sha256(string.encode("utf-8")).hexdigest()


def sha256_six_int(string):
    return str(int(sha256(string), 16) * 1000000)[0:6]


def send_verification(to=[], code="000000", debug=False):
    # login info
    server = "smtp.qq.com"
    port = 465
    user = "i@kokecacao.me"
    password = "hxgttnbbvzrcffjh"

    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = dir_path.split("/project")[0]  # should be ~/deep_vocab

    with open(dir_path + "/project/html/verification.html") as file:
        html = file.read()
        html = html.replace("$$six_digit_code$$", code)
        msg = MIMEText(html, 'html')

    # these are provided by SMTP sender
    # msg["Message-ID"] = "ID"
    # msg["In-Reply-To"] = "ID"
    # msg["References"] = "ID"
    msg['Content-Type'] = "text/html; charset=utf-8"
    msg['From'] = "{name} <{from_mail}>".format(name="Deep Vocab",
                                                from_mail=user)
    msg['To'] = ", ".join(to)
    msg['Subject'] = "Your Verification Code for Registeration"
    msg['Date'] = email.utils.formatdate(localtime=True)
    msg['Accept-Language'] = 'en-US'
    msg['Content-Language'] = 'en-US'
    msg['List-Unsubscribe-Post'] = 'List-Unsubscribe=One-Click'
    msg['List-Unsubscribe'] = '<https://kokecacao.me/unsubscribe/{id}>'.format(
        id="+".join(to))

    # # this method only for EmailMessage
    # msg.set_content("Testing Email Body 2")

    # See: https://vimsky.com/examples/detail/python-method-email.Utils.formatdate.html
    # with open('ExampleDoc.pdf', 'rb') as pdf:
    #     msg.add_attachment(pdf.read(), maintype='application', subtype='octet-stream', filename=pdf.name)
    try:
        if debug:
            print(msg.as_string())
        else:
            with smtplib.SMTP_SSL(server, port) as smtp:
                smtp.ehlo()
                smtp.login(user, password)
                smtp.sendmail(user, to, msg.as_string())
    except:
        return False
    return True


def send_change_password(to=[], code="000000", debug=False):
    # login info
    server = "smtp.qq.com"
    port = 465
    user = "i@kokecacao.me"
    password = "hxgttnbbvzrcffjh"

    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = dir_path.split("/project")[0]  # should be ~/deep_vocab

    with open(dir_path + "/project/html/recover.html") as file:
        html = file.read()
        html = html.replace("$$six_digit_code$$", code)
        msg = MIMEText(html, 'html')

    # these are provided by SMTP sender
    # msg["Message-ID"] = "ID"
    # msg["In-Reply-To"] = "ID"
    # msg["References"] = "ID"
    msg['Content-Type'] = "text/html; charset=utf-8"
    msg['From'] = "{name} <{from_mail}>".format(name="Deep Vocab",
                                                from_mail=user)
    msg['To'] = ", ".join(to)
    msg['Subject'] = "Your Verification Code for Recover Password"
    msg['Date'] = email.utils.formatdate(localtime=True)
    msg['Accept-Language'] = 'en-US'
    msg['Content-Language'] = 'en-US'
    msg['List-Unsubscribe-Post'] = 'List-Unsubscribe=One-Click'
    msg['List-Unsubscribe'] = '<https://kokecacao.me/unsubscribe/{id}>'.format(
        id="+".join(to))

    try:
        if debug:
            print(msg.as_string())
        else:
            with smtplib.SMTP_SSL(server, port) as smtp:
                smtp.ehlo()
                smtp.login(user, password)
                smtp.sendmail(user, to, msg.as_string())
    except:
        return False
    return True