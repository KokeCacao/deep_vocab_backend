import graphene

from .model import db


class UserVocab(graphene.ObjectType):
    id = graphene.Int()
    uuid = graphene.UUID()
    vocab_id = graphene.String()
    nth_word = graphene.Int()
    nth_appear = graphene.Int()
    edited_meaning = graphene.String()
    book_marked = graphene.Boolean()
    question_mark = graphene.Boolean()
    star_mark = graphene.Boolean()
    pin_mark = graphene.Boolean()
    added_mark = graphene.Boolean()


class UserVocabDB(db.Model):
    """ DATABASE FORMAT
    id: int; key; non-null; auto-increment;
    uuid: str(36); non-null; non-unique; foreign-key("authDB.uuid");
    vocab_id = str(36); non-null; non-unique; foreign-key("???"); # TODO: add foreign key connecting vocab list
    nth_word = int; non-unique; default(0); # TODO: add default value to other columns in other database where needed
    nth_appear = int; non-unique; default(0);
    edited_meaning = text; non-unique; null;
    book_marked = bool; non-unique; default(false);
    question_mark = bool; non-unique; default(false);
    star_mark = bool; non-unique; default(false);
    pin_mark = bool; non-unique; default(false);
    added_mark = bool; non-unique; default(false);
    """
    __tablename__ = 'userVocabDB'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    uuid = db.Column(db.String(36),
                     db.ForeignKey("authDB.uuid"),
                     nullable=False)
    vocab_id = db.Column(
        db.String(36),
        nullable=False)  # TODO: add foreign key connecting vocab list
    # for questions about default: https://www.coder.work/article/6205865
    nth_word = db.Column(db.Integer, default=0)
    nth_appear = db.Column(db.Integer, default=0)
    edited_meaning = db.Column(db.Text, nullable=True)
    book_marked = db.Column(db.Boolean, default=False)
    question_mark = db.Column(db.Boolean, default=False)
    star_mark = db.Column(db.Boolean, default=False)
    pin_mark = db.Column(db.Boolean, default=False)
    added_mark = db.Column(db.Boolean, default=False)

    auth_db = db.relationship("AuthDB", back_populates="user_vocab_db")

    # TODO: add foreign key connecting vocab list

    def __init__(self, id, uuid, vocab_id, nth_word, nth_appear,
                 edited_meaning, book_marked, question_mark, star_mark,
                 pin_mark, added_mark):
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

    def to_graphql_object(self):
        return UserVocab(
            id=self.id,
            uuid=self.uuid,
            vocab_id=self.vocab_id,
            nth_word=self.nth_word,
            nth_appear=self.nth_appear,
            edited_meaning=self.edited_meaning,
            book_marked=self.book_marked,
            question_mark=self.question_mark,
            star_mark=self.star_mark,
            pin_mark=self.pin_mark,
            added_mark=self.added_mark,
        )

    @staticmethod
    def add(uuid, vocab_id, nth_word, nth_appear, edited_meaning, book_marked,
            question_mark, star_mark, pin_mark, added_mark):
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
        )
        db.session.add(user_vocab_db)
        return user_vocab_db

    @staticmethod
    def get(id):
        return UserVocabDB.query.get(id)

    @staticmethod
    def get_by_uuid_vocab_id(uuid, vocab_id):
        q = UserVocabDB.query.filter(UserVocabDB.uuid == uuid).filter(
            UserVocabDB.vocab_id == vocab_id)
        assert (q.count() <= 1)
        return q.first()

    # TODO: turn all Exception here into InternalServerError, and check other model and calls to update functions
    @staticmethod
    def update(user_vocab_db, **kwargs):
        assert (user_vocab_db is not None)
        if 'id' in kwargs: raise Exception("400|[Warning] id can't be changed")
        if 'vocab_id' in kwargs:
            raise Exception("400|[Warning] vocab_id can't be changed")
        if 'uuid' in kwargs:
            raise Exception("400|[Warning] uuid can't be changed")
        if 'nth_word' in kwargs:
            raise Exception("400|[Warning] uuid can't be changed")
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
        return user_vocab_db
