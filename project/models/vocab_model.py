import graphene
import enum
from sqlalchemy.sql.expression import or_
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType

from .model import db


class TypeModel(enum.Enum):
    # See: https://en.wikipedia.org/wiki/Part_of_speech
    # noun
    # pronoun
    # verb
    # adjective
    # adverb
    # preposition
    # conjunction
    # interjection
    # article or (more recently) determiner
    n = "n"
    pron = "pron"
    v = "v"
    adj = "adj"
    adv = "adv"
    prep = "prep"
    conj = "conj"
    interj = "interj"
    art = "art"


class Vocab(graphene.ObjectType):
    vocab_id = graphene.String()
    edition = graphene.DateTime()
    list_ids = graphene.List(graphene.Int)
    vocab = graphene.String()
    type = graphene.Enum.from_enum(TypeModel)()
    main_translation = graphene.String()
    other_translation = graphene.List(graphene.String)
    main_sound = graphene.String()
    other_sound = graphene.List(graphene.String)
    english_translation = graphene.String()
    # "comments" field deprecated, do fetch "comments" in other queries
    confusing_word_id = graphene.List(graphene.String)
    # TODO: refactor this field to "confusing_words", fetch "vocab_id" only when user click on it
    mem_tips = graphene.String()
    example_sentences = graphene.List(graphene.String)


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
    confusing_word_id: list(str(36)); non-unique; null;
    mem_tips: text; non-unique; null;
    example_sentences: list(text); non-unique; null; # TODO: list of text??
    """
    __tablename__ = 'vocabDB'
    vocab_id = db.Column(db.String(36), primary_key=True, nullable=False)
    edition = db.Column(db.DateTime, nullable=False)
    list_ids = db.Column(MutableList.as_mutable(PickleType))  # db.Integer
    vocab = db.Column(db.String(120), nullable=False)
    type = db.Column(db.Enum(TypeModel), nullable=True)
    main_translation = db.Column(db.Text, nullable=True)
    other_translation = db.Column(
        MutableList.as_mutable(PickleType),  # db.String(120)
        nullable=True)
    main_sound = db.Column(db.String(120), nullable=False)
    other_sound = db.Column(
        MutableList.as_mutable(PickleType),  # db.String(120)
        nullable=True)
    english_translation = db.Column(db.Text, nullable=True)
    confusing_word_id = db.Column(
        MutableList.as_mutable(PickleType),  # db.String(36)
        nullable=True)
    mem_tips = db.Column(db.Text, nullable=True)
    example_sentences = db.Column(
        MutableList.as_mutable(PickleType),  # db.Text
        nullable=True)

    def __init__(self, vocab_id, edition, list_ids, vocab, type,
                 main_translation, other_translation, main_sound, other_sound,
                 english_translation, confusing_word_id, mem_tips,
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
        self.confusing_word_id = confusing_word_id
        self.mem_tips = mem_tips
        self.example_sentences = example_sentences

    def to_graphql_object(self):
        return Vocab(
            vocab_id=self.vocab_id,
            edition=self.edition,
            list_ids=self.list_ids,
            vocab=self.vocab,
            type=self.type,
            main_translation=self.main_translation,
            other_translation=self.other_translation,
            main_sound=self.main_sound,
            other_sound=self.other_sound,
            english_translation=self.english_translation,
            confusing_word_id=self.confusing_word_id,
            mem_tips=self.mem_tips,
            example_sentences=self.example_sentences,
        )

    @staticmethod
    def add(vocab_id, edition, list_ids, vocab, type, main_translation,
            other_translation, main_sound, other_sound, english_translation,
            confusing_word_id, mem_tips, example_sentences):
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
            confusing_word_id=confusing_word_id,
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
        raise NotImplementedError("400|Update Vocab Model Not Supported")
