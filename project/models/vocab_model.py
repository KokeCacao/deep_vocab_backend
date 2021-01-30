from sqlalchemy.sql.expression import or_
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType

from .model import db, TypeModel


class VocabDB(db.Model):
    """ DATABASE FORMAT
    vocab_id: str(36); key; non-null;
    edition: date_time; non-unique; non-null;
    list_ids: list(int); non-unique; non-null;
    vocab: str(120); non-unique; non-null;
    type: enum; non-unique; null;
    main_translation: text; non-unique; null;
    other_translation: list(str(120)); non-unique; null;
    main_sound: str(120); non-unique; null;
    other_sound: list(str(120)); non-unique; null;
    english_translation: text; non-unique; null;
    confusing_words: list(str(36)); non-unique; null;
    mem_tips: text; non-unique; null;
    example_sentences: list(text); non-unique; null;
    """
    __tablename__ = 'vocabDB'
    vocab_id = db.Column(db.String(36), primary_key=True, nullable=False)
    edition = db.Column(db.DateTime, nullable=False)
    list_ids = db.Column(MutableList.as_mutable(PickleType))  # db.Integer
    vocab = db.Column(db.String(120), nullable=False)
    type = db.Column(db.Enum(TypeModel), nullable=True)
    main_translation = db.Column(db.Text, nullable=True)
    other_translation = db.Column(MutableList.as_mutable(PickleType),
                                  nullable=True)
    main_sound = db.Column(db.String(120), nullable=False)
    other_sound = db.Column(MutableList.as_mutable(PickleType), nullable=True)
    english_translation = db.Column(db.Text, nullable=True)
    confusing_words = db.Column(MutableList.as_mutable(PickleType),
                                nullable=True)
    mem_tips = db.Column(db.Text, nullable=True)
    example_sentences = db.Column(MutableList.as_mutable(PickleType),
                                  nullable=True)

    mark_color_db = db.relationship("MarkColorDB", back_populates="vocab_db")
    user_vocab_db = db.relationship("UserVocabDB", back_populates="vocab_db")

    def __init__(self, vocab_id, edition, list_ids, vocab, type,
                 main_translation, other_translation, main_sound, other_sound,
                 english_translation, confusing_words, mem_tips,
                 example_sentences):
        self.vocab_id = vocab_id
        self.edition = edition
        self.list_ids = list_ids
        self.vocab = vocab
        self.type = type
        self.main_translation = main_translation
        self.other_translation = other_translation
        self.main_sound = main_sound
        self.other_sound = other_sound
        self.english_translation = english_translation
        self.confusing_words = confusing_words
        self.mem_tips = mem_tips
        self.example_sentences = example_sentences

    @staticmethod
    def add(vocab_id, edition, list_ids, vocab, type, main_translation,
            other_translation, main_sound, other_sound, english_translation,
            confusing_words, mem_tips, example_sentences):
        vocab_db = VocabDB(
            vocab_id=vocab_id,
            edition=edition,
            list_ids=list_ids,
            vocab=vocab,
            type=type,
            main_translation=main_translation,
            other_translation=other_translation,
            main_sound=main_sound,
            other_sound=other_sound,
            english_translation=english_translation,
            confusing_words=confusing_words,
            mem_tips=mem_tips,
            example_sentences=example_sentences,
        )
        db.session.add(vocab_db)
        return vocab_db

    @staticmethod
    def get(vocab_id):
        return VocabDB.query.get(vocab_id)

    @staticmethod
    def gets(vocab_ids, sorted=False):
        result = VocabDB.query.filter(
            or_(*[VocabDB.vocab_id == x for x in vocab_ids]))
        if sorted: return result.order_by(VocabDB.vocab.asc()).all()
        else: return result.all()

    @staticmethod
    def update(user_vocab_db, **kwargs):
        # TODO
        raise NotImplementedError("Update Vocab Model Not Supported.")
