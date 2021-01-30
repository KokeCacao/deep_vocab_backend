import graphene

from ..models.model import db
from ..models.vocab_model import VocabDB, TypeModel, Vocab
from ..models.mark_color_model import MarkColorDB


class TestMutation(graphene.Mutation):
    """
    mutation {
        test(key: "Koke_Cacao 's secret key", action: "add to db") {
            success
        }
    }
    """
    class Arguments:
        key = graphene.String(required=True)
        action = graphene.String(required=True)

    success = graphene.Boolean()

    @staticmethod
    def mutate(parent, info, **kwargs):
        key = kwargs["key"]
        action = kwargs["action"]

        if key != "Koke_Cacao 's secret key":
            raise Exception("400|Invalid Key")
        if action == "add to db":
            from datetime import datetime
            for vocab_int in range(1, 100):
                vocab_id = str(vocab_int)
                vocab_db = vocab_db = VocabDB.get(vocab_id)
                if vocab_db == None:
                    vocab_db = VocabDB.add(
                        vocab_id=vocab_id,
                        edition=datetime.now(),
                        list_ids=[0, 1],
                        vocab="vocab" + vocab_id,
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
                else:
                    raise Exception("400|Already Added")
            db.session.commit()
        return TestMutation(success=True)
