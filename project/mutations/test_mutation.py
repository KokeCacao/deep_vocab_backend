import graphene

from ..models.model import db
from ..models.vocab_model import VocabDB, TypeModel, Vocab
from ..models.mark_color_model import MarkColorDB


class TestMutation(graphene.Mutation):
    """
    mutation {
        test(edition: "2021-01-23T02:26:15.196899") {
            vocab {
                vocabId
                edition
                listIds
                vocab
                type
                mainTranslation
                otherTranslation
                mainSound
                otherSound
                englishTranslation
                confusingWordId
                memTips
                exampleSentences
            }
        }
    }
    """
    class Arguments:
        edition = graphene.DateTime(required=True)

    # vocab = graphene.Field(Vocab)
    vocab = graphene.List(Vocab)

    @staticmethod
    def mutate(parent, info, **kwargs):
        vocab_db = vocab_db = VocabDB.get("1")
        if vocab_db == None:
            vocab_db = VocabDB.add(
                vocab_id="1",
                edition=kwargs["edition"],
                list_ids=[0, 1],
                vocab="vocab",
                type=TypeModel.adj,
                main_translation="main_translation",
                other_translation=["other_translation"],
                main_sound="main_sound",
                other_sound=["other_sound", "other_sound"],
                english_translation="english_translation",
                confusing_word_id=["confusing_word_id"],
                mem_tips="mem_tips",
                example_sentences=["example_sentences"],
            )
            db.session.commit()
        else:
            mark_color_dbs = MarkColorDB.get_by_uuid(
                "2d1a11b9-0d11-4c1e-9767-35f3deeffee2")
            mark_color_dbs.sort(key=lambda mark_color_db: mark_color_db.time,
                                reverse=False)
            vocab_dict = dict()
            for mark_color_db in mark_color_dbs:
                mark_colors = vocab_dict.setdefault(mark_color_db.vocab_id, [])
                mark_colors.append(mark_color_db.color)
                vocab_dict[mark_color_db.vocab_id] = mark_colors

            print("keys = ")
            for key in vocab_dict.keys():
                print("{}: {}".format(key, vocab_dict[key]))
        # return TestMutation(vocab=vocab_db.to_graphql_object())
        return TestMutation(vocab=[vocab_db.to_graphql_object()])
