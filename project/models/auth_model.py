import graphene
from werkzeug.exceptions import InternalServerError
from .model import db


class Auth(graphene.ObjectType):
    uuid = graphene.UUID()
    email = graphene.String()
    user_name = graphene.String()
    password = graphene.String()
    access_token = graphene.String()
    refresh_token = graphene.String()
    wx_token = graphene.String()


class AuthDB(db.Model):
    """ DATABASE FORMAT
    uuid: str(36); key; non-null;
    email: str(120); unique; non-null;
    user_name: str(80); unique; non-null;
    password: str(120); unique; non-null;
    access_token: str(120); non-unique; null;
    refresh_token: str(120); non-unique; null;
    wx_token: str(120); non-unique; null;
    """
    __tablename__ = 'authDB'
    uuid = db.Column(db.String(36), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    user_name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False, nullable=False)
    access_token = db.Column(db.String(120), unique=False, nullable=True)
    refresh_token = db.Column(db.String(120), unique=False, nullable=True)
    wx_token = db.Column(db.String(120), unique=False, nullable=True)

    user_db = db.relationship("UserDB", back_populates="auth_db")
    mark_color_db = db.relationship("MarkColorDB", back_populates="auth_db")
    user_vocab_db = db.relationship("UserVocabDB", back_populates="auth_db")

    def __init__(self, uuid, user_name, password, email, access_token,
                 refresh_token, wx_token):
        self.uuid = uuid
        self.user_name = user_name
        self.password = password
        self.email = email
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.wx_token = wx_token

    @staticmethod
    def add(uuid, user_name, password, email, access_token, refresh_token,
            wx_token):
        assert AuthDB.get(uuid) is None
        auth_db = AuthDB(uuid=uuid,
                         user_name=user_name,
                         password=password,
                         email=email,
                         access_token=access_token,
                         refresh_token=refresh_token,
                         wx_token=wx_token)
        db.session.add(auth_db)
        return auth_db

    @staticmethod
    def get(uuid):
        return AuthDB.query.get(uuid)

    @staticmethod
    def get_by_user_name(user_name):
        q = AuthDB.query.filter(AuthDB.user_name == user_name)
        assert q.count() <= 1
        return q.first()

    @staticmethod
    def get_by_email(email):
        q = AuthDB.query.filter(AuthDB.email == email)
        assert q.count() <= 1
        return q.first()

    @staticmethod
    def update(user_db, **kwargs):
        assert user_db is not None
        if 'uuid' in kwargs:
            raise InternalServerError("[AuthModel] uuid can't be changed.")
        if 'user_name' in kwargs:
            raise InternalServerError(
                "[AuthModel] user_name can't be changed.")
        if 'password' in kwargs: user_db.password = kwargs['password']
        if 'email' in kwargs: user_db.email = kwargs['email']
        if 'access_token' in kwargs:
            user_db.access_token = kwargs['access_token']
        if 'refresh_token' in kwargs:
            user_db.refresh_token = kwargs['refresh_token']
        if 'wx_token' in kwargs: user_db.wx_token = kwargs['wx_token']
        return user_db
