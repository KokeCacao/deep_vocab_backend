import graphene
import enum

from .model import db


class ColorModel(enum.Enum):
    black = "black"
    red = "red"
    yellow = "yellow"
    green = "green"


class MarkColor(graphene.ObjectType):
    # if resolver not specified, use default resolver
    # see https://docs.graphene-python.org/en/latest/types/objecttypes/#defaultresolver
    id = graphene.Int()
    vocab_id = graphene.String()
    uuid = graphene.UUID()
    index = graphene.Int()
    # See: https://docs.graphene-python.org/en/latest/types/enums/, example: https://github.com/graphql-python/graphene/issues/273
    color = graphene.Enum.from_enum(ColorModel)()
    # See: https://docs.graphene-python.org/en/latest/types/scalars/
    time = graphene.DateTime()


class MarkColorDB(db.Model):
    """ DATABASE FORMAT
    id: int; key; auto-increment;
    vocab_id = str(36); non-null; non-unique; foreign-key("???"); # TODO: add foreign key connecting vocab list
    uuid: str(36); non-null; non-unique; foreign-key("authDB.uuid");
    index: int; non-unique; non-null;
    color: enum; non-unique; non-null;
    time: date_time; non-unique; non-null;
    """
    __tablename__ = 'markColorDB'
    # Note: SQLAlchemy will automatically set the first Integer Primary Key(PK)
    # column that's not marked as a Foreign Key (FK) as autoincrement=True
    # Therefore, autoincrement=True should not be specified.
    # Set id field to null when adding to database.
    id = db.Column(db.Integer, primary_key=True)
    vocab_id = db.Column(db.String(36), nullable=False)
    uuid = db.Column(db.String(36), db.ForeignKey("authDB.uuid"))
    index = db.Column(db.Integer, nullable=False)
    color = db.Column(db.Enum(ColorModel), nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    auth_db = db.relationship("AuthDB", back_populates="mark_color_db")

    # TODO: add foreign key connecting vocab list

    def __init__(self, id, vocab_id, uuid, index, color, time):
        self.id = id
        self.vocab_id = vocab_id
        self.uuid = uuid
        self.index = index
        self.color = color
        self.time = time

    def to_graphql_object(self):
        return MarkColor(id=self.id,
                         vocab_id=self.vocab_id,
                         uuid=self.uuid,
                         index=self.index,
                         color=self.color,
                         time=self.time)

    @staticmethod
    def add(vocab_id, uuid, index, color, time):
        mark_color_db = MarkColorDB(id=None,
                                    uuid=uuid,
                                    vocab_id=vocab_id,
                                    index=index,
                                    color=color,
                                    time=time)
        db.session.add(mark_color_db)
        return mark_color_db

    @staticmethod
    def get(id):
        return MarkColorDB.query.get(id)

    @staticmethod
    def get_by_uuid(uuid):
        return MarkColorDB.query.filter(MarkColorDB.uuid == uuid).all()

    @staticmethod
    def get_by_uuid_vocab_id(uuid, vocab_id):
        return MarkColorDB.query.filter(MarkColorDB.uuid == uuid).filter(
            MarkColorDB.vocab_id == vocab_id).all()

    @staticmethod
    def get_by_uuid_vocab_id_index(uuid, vocab_id, index):
        q = MarkColorDB.query.filter(MarkColorDB.uuid == uuid).filter(
            MarkColorDB.vocab_id == vocab_id).filter(
                MarkColorDB.index == index)
        assert (q.count() <= 1)
        return q.first()

    @staticmethod
    def update(mark_color_db, **kwargs):
        assert (mark_color_db is not None)
        if 'id' in kwargs: raise Exception("400|[Warning] id can't be changed")
        if 'vocab_id' in kwargs:
            raise Exception("400|[Warning] vocab_id can't be changed")
        if 'uuid' in kwargs:
            raise Exception("400|[Warning] uuid can't be changed")
        if 'index' in kwargs:
            raise Exception("400|[Warning] index can't be changed")
        if 'color' in kwargs: mark_color_db.color = kwargs['color']
        if 'time' in kwargs: mark_color_db.time = kwargs['time']
        return mark_color_db
