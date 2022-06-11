import graphene
import enum

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

    # graphene.Enum.from_enum(ColorModel) can't be used twice without storing the value
    # See: https://github.com/graphql-python/graphene-sqlalchemy/issues/211
    from functools import lru_cache
    graphene.Enum.from_enum = lru_cache(maxsize=None)(graphene.Enum.from_enum)
    color = graphene.Enum.from_enum(ColorModel)()

    # See: https://docs.graphene-python.org/en/latest/types/scalars/
    time = graphene.DateTime()


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
    confusing_words = graphene.List(graphene.String)
    mem_tips = graphene.String()
    example_sentences = graphene.List(graphene.String)


class VocabListHeader(graphene.ObjectType):
    name = graphene.String()
    list_id = graphene.Int()
    edition = graphene.DateTime()
    vocab_ids = graphene.List(graphene.String)


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
    mark_colors = graphene.List(MarkColor)


class VocabUserVocab(Vocab, UserVocab):
    def from_vocab_and_user_vocab(self, vocab, user_vocab, mark_colors_list):
        if vocab is not None:
            self.vocab_id = vocab.vocab_id
            self.edition = vocab.edition
            self.list_ids = vocab.list_ids
            self.vocab = vocab.vocab
            self.type = vocab.type
            self.main_translation = vocab.main_translation
            self.other_translation = vocab.other_translation
            self.main_sound = vocab.main_sound
            self.other_sound = vocab.other_sound
            self.english_translation = vocab.english_translation
            self.confusing_words = vocab.confusing_words
            self.mem_tips = vocab.mem_tips
            self.example_sentences = vocab.example_sentences
        if user_vocab is not None:
            self.nth_word = user_vocab.nth_word
            self.nth_appear = user_vocab.nth_appear
            self.edited_meaning = user_vocab.edited_meaning
            self.book_marked = user_vocab.book_marked
            self.question_mark = user_vocab.question_mark
            self.star_mark = user_vocab.star_mark
            self.pin_mark = user_vocab.pin_mark
            self.added_mark = user_vocab.added_mark
        else:
            # Initialization to client when no record on database
            self.nth_word = 0
            self.nth_appear = 0
            self.book_marked = False
            self.question_mark = False
            self.star_mark = False
            self.pin_mark = False
            self.added_mark = False
        if mark_colors_list is not None and mark_colors_list != []:
            self.mark_colors = mark_colors_list
        return self