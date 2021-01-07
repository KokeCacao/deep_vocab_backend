import graphene
from .model import db


class User(graphene.ObjectType):
    # if resolver not specified, use default resolver
    # see https://docs.graphene-python.org/en/latest/types/objecttypes/#defaultresolver
    uuid = graphene.UUID()
    display_name = graphene.String()
    user_name = graphene.String()
    avatar_url = graphene.String()
    level = graphene.Int()
    xp = graphene.Int()


class UserDB(db.Model):
    """ DATABASE FORMAT
    uuid: str(36); key; non-null;
    display_name: str(120); null;
    user_name: str(80); unique; null;
    avatar_url: str(120); non-unique; null;
    level: int; non-unique; 0;
    xp: int; non-unique; 0;
    """
    __tablename__ = 'userDB'
    uuid = db.Column(db.String(36),
                     db.ForeignKey("authDB.uuid"),
                     primary_key=True)
    display_name = db.Column(db.String(120))
    user_name = db.Column(db.String(80), unique=True)
    avatar_url = db.Column(db.String(120))
    level = db.Column(db.Integer)
    xp = db.Column(db.Integer)

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

    def to_graphql_object(self):
        return User(uuid=self.uuid,
                    display_name=self.display_name,
                    user_name=self.user_name,
                    avatar_url=self.avatar_url,
                    level=self.level,
                    xp=self.xp)

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
        """ UPDATE
        user_db: UserDB.get(kwargs['uuid'])
        **kwargs: passed by query arguments

        1. when updating, we only change what you passed to us
        therefore, if you want to set it to empty, you can use None
        2. you can update everything if it is not a key
        """
        assert (user_db is not None)
        if 'user_name' in kwargs: user_db.user_name = kwargs['user_name']
        if 'display_name' in kwargs:
            user_db.display_name = kwargs['display_name']
        if 'avatar_url' in kwargs: user_db.avatar_url = kwargs['avatar_url']
        if 'level' in kwargs: user_db.level = kwargs['level']
        if 'xp' in kwargs: user_db.xp = kwargs['xp']
        return user_db
