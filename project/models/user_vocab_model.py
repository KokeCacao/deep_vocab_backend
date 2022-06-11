from datetime import datetime
from sqlalchemy.sql.expression import or_
from werkzeug.exceptions import InternalServerError
from database import db


class UserVocabDB(db.Model):
    """ DATABASE FORMAT
    id: int; key; non-null; auto-increment;
    uuid: str(36); non-null; non-unique; foreign-key("authDB.uuid");
    vocab_id = str(36); non-null; non-unique; foreign-key("vocabDB.vocab_id");
    nth_word = int; non-unique; default(0);
    nth_appear = int; non-unique; default(0);
    edited_meaning = text; non-unique; null;
    book_marked = bool; non-unique; default(false);
    question_mark = bool; non-unique; default(false);
    star_mark = bool; non-unique; default(false);
    pin_mark = bool; non-unique; default(false);
    added_mark = bool; non-unique; default(false);
    long_term_mem = int; non-unique; default(0);
    refresh_time = date_time; non-unique; non-null;
    """
    __tablename__ = 'userVocabDB'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    uuid = db.Column(db.String(36),
                     db.ForeignKey("authDB.uuid"),
                     nullable=False)
    vocab_id = db.Column(db.String(36), db.ForeignKey("vocabDB.vocab_id"))
    # for questions about default: https://www.coder.work/article/6205865
    nth_word = db.Column(db.Integer, default=0)
    nth_appear = db.Column(db.Integer, default=0)
    edited_meaning = db.Column(db.Text, nullable=True)
    book_marked = db.Column(db.Boolean, default=False)
    question_mark = db.Column(db.Boolean, default=False)
    star_mark = db.Column(db.Boolean, default=False)
    pin_mark = db.Column(db.Boolean, default=False)
    added_mark = db.Column(db.Boolean, default=False)
    long_term_mem = db.Column(db.Float, default=0.0)
    refresh_time = db.Column(db.DateTime, default=datetime.utcnow)

    # See: https://stackoverflow.com/a/10061143/9569969
    # and https://stackoverflow.com/a/61745281/9569969
    db.UniqueConstraint(uuid, vocab_id)

    auth_db = db.relationship("AuthDB", back_populates="user_vocab_db")
    vocab_db = db.relationship("VocabDB", back_populates="user_vocab_db")

    def __init__(self, id, uuid, vocab_id, nth_word, nth_appear,
                 edited_meaning, book_marked, question_mark, star_mark,
                 pin_mark, added_mark, long_term_mem, refresh_time):
        self.id = id
        self.uuid = uuid
        self.vocab_id = vocab_id
        self.nth_word = nth_word
        self.nth_appear = nth_appear
        self.edited_meaning = edited_meaning
        self.book_marked = book_marked
        self.question_mark = question_mark
        self.star_mark = star_mark
        self.pin_mark = pin_mark
        self.added_mark = added_mark
        self.long_term_mem = long_term_mem
        self.refresh_time = refresh_time

    @staticmethod
    def add(uuid,
            vocab_id,
            nth_word=None,
            nth_appear=None,
            edited_meaning=None,
            book_marked=None,
            question_mark=None,
            star_mark=None,
            pin_mark=None,
            added_mark=None,
            long_term_mem=None,
            refresh_time=None):
        user_vocab_db = UserVocabDB(
            id=None,
            uuid=uuid,
            vocab_id=vocab_id,
            nth_word=nth_word,
            nth_appear=nth_appear,
            edited_meaning=edited_meaning,
            book_marked=book_marked,
            question_mark=question_mark,
            star_mark=star_mark,
            pin_mark=pin_mark,
            added_mark=added_mark,
            long_term_mem=long_term_mem,
            refresh_time=refresh_time,
        )
        db.session.add(user_vocab_db)
        return user_vocab_db

    @staticmethod
    def get(id):
        return UserVocabDB.query.get(id)

    @staticmethod
    def gets(vocab_ids):
        if len(vocab_ids) == 0: return []
        return UserVocabDB.query.filter(
            or_(*[UserVocabDB.vocab_id == x for x in vocab_ids])).all()

    @staticmethod
    def get_by_uuid(uuid, sorted=False):
        result = UserVocabDB.query.filter(UserVocabDB.uuid == uuid)
        if sorted: return result.order_by(UserVocabDB.refresh_time.asc()).all()
        else: return result.all()

    @staticmethod
    def get_by_uuid_vocab_id(uuid,
                             vocab_id,
                             with_for_update=False,
                             erase_cache=False):
        q = UserVocabDB.query.filter(UserVocabDB.uuid == uuid).filter(
            UserVocabDB.vocab_id == vocab_id)

        if with_for_update: q = q.with_for_update()
        if erase_cache: q = q.populate_existing()

        return q.first()

    # This function is untested
    @staticmethod
    def get_by_uuid_to_vocab_id_dict(uuid, sorted=False):
        user_vocab_dbs = UserVocabDB.get_by_uuid(uuid, sorted=sorted)

        # vocab_dict = {vocab_id: refresh_time}
        vocab_dict = dict()
        for user_vocab_db in user_vocab_dbs:
            vocab_dict[user_vocab_db.vocab_id] = user_vocab_db.refresh_time
        return vocab_dict

    @staticmethod
    def get_by_uuid_after_now(uuid,
                              sorted=False,
                              with_for_update=False,
                              erase_cache=False):
        q = UserVocabDB.query.filter(
            UserVocabDB.refresh_time < datetime.utcnow())

        if sorted: q = q.order_by(UserVocabDB.refresh_time.asc())
        if with_for_update: q = q.with_for_update()
        if erase_cache: q = q.populate_existing()

        return q.all()

    @staticmethod
    def update(user_vocab_db, **kwargs):
        if 'id' in kwargs:
            raise InternalServerError("[UserVocabModel] id can't be changed.")
        if 'uuid' in kwargs:
            raise InternalServerError(
                "[UserVocabModel] uuid can't be changed.")
        if 'vocab_id' in kwargs:
            raise InternalServerError(
                "[UserVocabModel] vocab_id can't be changed.")
        if 'nth_word' in kwargs:
            user_vocab_db.nth_word = kwargs['nth_word']
        if 'nth_appear' in kwargs:
            user_vocab_db.nth_appear = kwargs['nth_appear']
        if 'edited_meaning' in kwargs:
            user_vocab_db.edited_meaning = kwargs['edited_meaning']
        if 'book_marked' in kwargs:
            user_vocab_db.book_marked = kwargs['book_marked']
        if 'question_mark' in kwargs:
            user_vocab_db.question_mark = kwargs['question_mark']
        if 'star_mark' in kwargs: user_vocab_db.star_mark = kwargs['star_mark']
        if 'pin_mark' in kwargs: user_vocab_db.pin_mark = kwargs['pin_mark']
        if 'added_mark' in kwargs:
            user_vocab_db.added_mark = kwargs['added_mark']
        if 'long_term_mem' in kwargs:
            user_vocab_db.long_term_mem = kwargs['long_term_mem']
        if 'refresh_time' in kwargs:
            user_vocab_db.refresh_time = kwargs['refresh_time']
        return user_vocab_db
