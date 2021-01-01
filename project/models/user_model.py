import graphene
from .model import db


class User(graphene.ObjectType):
    # if resolver not specified, use default resolver
    # see https://docs.graphene-python.org/en/latest/types/objecttypes/#defaultresolver
    uuid = graphene.UUID()
    public_email = graphene.String()
    user_name = graphene.String()
    avatar_url = graphene.String()
    level = graphene.Int()
    xp = graphene.Int()

    @staticmethod
    def parse_kwargs(**kwargs):
        kwargs['uuid'] = str(kwargs['uuid'])
        print("[DEBUG] parsed kwargs = {}".format(kwargs))
        return kwargs


class UserDB(db.Model):
    """ DATABASE FORMAT
    uuid: str(36); key; non-null;
    public_email: str(120); unique; null;
    user_name: str(80); unique; null;
    avatar_url: str(120); non-unique; null;
    level: int; non-unique; 0;
    xp: int; non-unique; 0;
    """
    uuid = db.Column(db.String(36), primary_key=True)
    public_email = db.Column(db.String(120), unique=True)
    user_name = db.Column(db.String(80), unique=True)
    avatar_url = db.Column(db.String(120))
    level = db.Column(db.Integer)
    xp = db.Column(db.Integer)

    def __init__(self, uuid, user_name, public_email, avatar_url, level, xp):
        self.uuid = uuid
        self.user_name = user_name
        self.public_email = public_email
        self.avatar_url = avatar_url
        self.level = level
        self.xp = xp

    def to_graphql_object(self):
        return User(uuid=self.uuid,
                    public_email=self.public_email,
                    user_name=self.user_name,
                    avatar_url=self.avatar_url,
                    level=self.level,
                    xp=self.xp)

    @staticmethod
    def add(uuid,
            user_name=None,
            public_email=None,
            avatar_url=None,
            level=0,
            xp=0):
        assert (UserDB.get(uuid) is None)
        user_db = UserDB(uuid=uuid,
                         user_name=user_name,
                         public_email=public_email,
                         avatar_url=avatar_url,
                         level=level,
                         xp=xp)
        db.session.add(user_db)
        return user_db

    @staticmethod
    def get(uuid):
        return UserDB.query.get(uuid)

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
        if 'public_email' in kwargs:
            user_db.public_email = kwargs['public_email']
        if 'avatar_url' in kwargs: user_db.avatar_url = kwargs['avatar_url']
        if 'level' in kwargs: user_db.level = kwargs['level']
        if 'xp' in kwargs: user_db.xp = kwargs['xp']
        return user_db


from .. import app
with app.app_context():
    print("Creating Database for user_model.py")
    db.create_all()