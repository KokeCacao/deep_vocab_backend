from werkzeug.exceptions import InternalServerError
from .model import db


class UserDB(db.Model):
    """ DATABASE FORMAT
    uuid: str(36); key; non-null; foreign-key("authDB.uuid");
    display_name: str(120); null;
    user_name: str(80); unique; null;
    avatar_url: str(120); non-unique; null; # TODO: maybe increase the length to allow longer? or do internal storage
    level: int; non-unique; default(0);
    xp: int; non-unique; default(0);
    """
    __tablename__ = 'userDB'
    uuid = db.Column(db.String(36),
                     db.ForeignKey("authDB.uuid"),
                     primary_key=True)
    display_name = db.Column(db.String(120), nullable=True)
    user_name = db.Column(db.String(80), unique=True, nullable=True)
    avatar_url = db.Column(db.String(120), nullable=True)
    level = db.Column(db.Integer, default=0)
    xp = db.Column(db.Integer, default=0)

    # see: https://docs.sqlalchemy.org/en/13/orm/tutorial.html
    # or: https://docs.sqlalchemy.org/en/13/orm/backref.html#relationships-backref
    # or: http://docs.jinkan.org/docs/flask-sqlalchemy/models.html
    # Also the first argument should be class instead of table name:
    # See: https://stackoverflow.com/questions/25002620/argumenterror-relationship-expects-a-class-or-mapper-argument
    auth_db = db.relationship("AuthDB", back_populates="user_db")

    def __init__(self, uuid, user_name, display_name, avatar_url, level, xp):
        self.uuid = uuid
        self.user_name = user_name
        self.display_name = display_name
        self.avatar_url = avatar_url
        self.level = level
        self.xp = xp

    @staticmethod
    def add(uuid, user_name, display_name, avatar_url, level, xp):
        assert (UserDB.get(uuid) is None)
        user_db = UserDB(uuid=uuid,
                         user_name=user_name,
                         display_name=display_name,
                         avatar_url=avatar_url,
                         level=level,
                         xp=xp)
        db.session.add(user_db)
        return user_db

    @staticmethod
    def get(uuid):
        return UserDB.query.get(uuid)

    @staticmethod
    def get_by_user_name(user_name):
        return UserDB.query.filter(UserDB.user_name == user_name).first()

    @staticmethod
    def update(user_db, **kwargs):
        if 'uuid' in kwargs:
            raise InternalServerError("[UserModel] uuid can't be changed.")
        if 'user_name' in kwargs:
            raise InternalServerError(
                "[UserModel] user_name can't be changed.")
        if 'display_name' in kwargs:
            user_db.display_name = kwargs['display_name']
        if 'avatar_url' in kwargs: user_db.avatar_url = kwargs['avatar_url']
        if 'level' in kwargs: user_db.level = kwargs['level']
        if 'xp' in kwargs: user_db.xp = kwargs['xp']
        return user_db
