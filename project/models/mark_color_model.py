from werkzeug.exceptions import InternalServerError
from database import db
from .model import ColorModel


class MarkColorDB(db.Model):
    """ DATABASE FORMAT
    id: int; key; auto-increment;
    vocab_id = str(36); non-null; non-unique; foreign-key("vocabDB.vocab_id");
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
    vocab_id = db.Column(db.String(36), db.ForeignKey("vocabDB.vocab_id"))
    uuid = db.Column(db.String(36), db.ForeignKey("authDB.uuid"))
    index = db.Column(db.Integer, nullable=False)
    color = db.Column(db.Enum(ColorModel), nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    db.UniqueConstraint(uuid, vocab_id, index)

    auth_db = db.relationship("AuthDB", back_populates="mark_color_db")
    vocab_db = db.relationship("VocabDB", back_populates="mark_color_db")

    def __init__(self, id, vocab_id, uuid, index, color, time):
        self.id = id
        self.vocab_id = vocab_id
        self.uuid = uuid
        self.index = index
        self.color = color
        self.time = time

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
    def get_by_uuid(uuid, sorted=False):
        result = MarkColorDB.query.filter(MarkColorDB.uuid == uuid)
        if sorted: return result.order_by(MarkColorDB.time.asc()).all()
        else: return result.all()

    @staticmethod
    def get_by_uuid_vocab_id(uuid, vocab_id, sorted=False):
        result = MarkColorDB.query.filter(MarkColorDB.uuid == uuid).filter(
            MarkColorDB.vocab_id == vocab_id)
        if sorted: return result.order_by(MarkColorDB.time.asc()).all()
        else: return result.all()

    @staticmethod
    def get_by_uuid_to_vocab_id_dict(uuid, sorted=False):
        mark_color_dbs = MarkColorDB.get_by_uuid(uuid, sorted=sorted)

        # vocab_dict = {vocab_id: [MarkColor]}
        vocab_dict = dict()
        for mark_color_db in mark_color_dbs:
            mark_colors = vocab_dict.setdefault(mark_color_db.vocab_id, [])
            mark_colors.append(mark_color_db)
            vocab_dict[mark_color_db.vocab_id] = mark_colors
        return vocab_dict

    @staticmethod
    def get_by_uuid_vocab_id_index(uuid,
                                   vocab_id,
                                   index,
                                   with_for_update=False,
                                   erase_cache=False):
        q = MarkColorDB.query.filter(MarkColorDB.uuid == uuid).filter(
            MarkColorDB.vocab_id == vocab_id).filter(
                MarkColorDB.index == index)

        if with_for_update: q = q.with_for_update()
        if erase_cache: q = q.populate_existing()

        return q.first()

    # not used
    @staticmethod
    def get_by_uuid_time_interval(uuid, from_time, to_time, sorted=False):
        result = MarkColorDB.query.filter(MarkColorDB.uuid == uuid).filter(
            MarkColorDB.time > from_time).filter(MarkColorDB.time < to_time)
        if sorted: return result.order_by(MarkColorDB.time.asc()).all()
        else: return result.all()

    @staticmethod
    def update(mark_color_db, **kwargs):
        if 'id' in kwargs:
            raise InternalServerError("[MarkColorModel] id can't be changed.")
        if 'vocab_id' in kwargs:
            raise InternalServerError(
                "[MarkColorModel] vocab_id can't be changed.")
        if 'uuid' in kwargs:
            raise InternalServerError(
                "[MarkColorModel] uuid can't be changed.")
        if 'index' in kwargs:
            raise InternalServerError(
                "[MarkColorModel] index can't be changed.")
        if 'color' in kwargs: mark_color_db.color = kwargs['color']
        if 'time' in kwargs: mark_color_db.time = kwargs['time']
        return mark_color_db
