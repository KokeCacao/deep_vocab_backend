import graphene
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
    email: str(120); unique; null;
    user_name: str(80); unique; null;
    password: str(120); unique; null;
    access_token: str(120); non-unique; null;
    refresh_token: str(120); non-unique; null;
    wx_token: str(120); non-unique; null;
    """
    __tablename__ = 'authDB'
    uuid = db.Column(db.String(36), primary_key=True)
    email = db.Column(db.String(120), unique=True)
    user_name = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120), unique=False)
    access_token = db.Column(db.String(120), unique=False)
    refresh_token = db.Column(db.String(120), unique=False)
    wx_token = db.Column(db.String(120), unique=False)

    user_db = db.relationship("UserDB", back_populates="auth_db")
    mark_color_db = db.relationship("MarkColorDB", back_populates="auth_db")

    def __init__(self, uuid, user_name, password, email, access_token,
                 refresh_token, wx_token):
        self.uuid = uuid
        self.user_name = user_name
        self.password = password
        self.email = email
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.wx_token = wx_token

    def to_graphql_object(self):
        return Auth(uuid=self.uuid,
                    email=self.email,
                    user_name=self.user_name,
                    password=self.password,
                    access_token=self.access_token,
                    refresh_token=self.refresh_token,
                    wx_token=self.wx_token)

    @staticmethod
    def add(uuid, user_name, password, email, access_token, refresh_token,
            wx_token):
        assert (AuthDB.get(uuid) is None)
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
        assert (q.count() <= 1)
        return q.first()

    @staticmethod
    def get_by_email(email):
        q = AuthDB.query.filter(AuthDB.email == email)
        assert (q.count() <= 1)
        return q.first()

    @staticmethod
    def update(user_db, **kwargs):
        assert (user_db is not None)
        if 'user_name' in kwargs: user_db.user_name = kwargs['user_name']
        if 'password' in kwargs: user_db.password = kwargs['password']
        if 'email' in kwargs: user_db.email = kwargs['email']
        if 'access_token' in kwargs:
            user_db.access_token = kwargs['access_token']
        if 'refresh_token' in kwargs:
            user_db.refresh_token = kwargs['refresh_token']
        if 'wx_token' in kwargs: user_db.wx_token = kwargs['wx_token']
        return user_db
