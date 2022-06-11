import pandas as pd
from tqdm import tqdm
from database import args  # app here refers to app.py, but Flask()

from ..models.vocab_model import VocabDB, TypeModel
from datetime import datetime
from flask import current_app


def add_dymmy_to_database():
    for vocab_int in range(1, 100):
        vocab_id = str(vocab_int)
        vocab_db = vocab_db = VocabDB.get(vocab_id)
        if vocab_db == None:
            vocab_db = VocabDB.add(
                vocab_id=vocab_id,
                edition=datetime.utcnow(),
                list_ids=[0, 1],
                vocab="vocab" + vocab_id,
                type=TypeModel.adj,
                main_translation="main_translation",
                other_translation=["other_translation"],
                main_sound="main_sound",
                other_sound=["other_sound", "other_sound"],
                english_translation="english_translation",
                confusing_words=["confusing_words"],
                mem_tips="mem_tips",
                example_sentences=["example_sentences"],
            )
        else:
            raise Exception("400|[Warning] already added")


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]

    return inner


@singleton
class BarronDatabaseCreator:

    path = args.csv
    list_id = 0
    list_header = {
        "name": "Barron3500",
        "list_id": list_id,
        "edition": None,
        "vocab_ids": set()
    }

    def __init__(self):
        pass

    def get_header(self):
        if len(self.list_header["vocab_ids"]) == 0:
            self.add_barron_to_database(only_iterate=True)

        return self.list_id, self.list_header

    def read_csv(self, path):
        df = pd.read_csv(path)

        del df["number"]
        del df["Check"]
        del df["Color"]
        del df["Random"]
        del df["RandomNum"]
        del df["indexnumber"]
        del df["Englishall"]

        del df["Word"]

        df = df.dropna(subset=[
            "Vocab", "Type", "VocabMeaning1", "Translate",
            "EnglishTranslation", "EnglishSentence", "Pronounce1"
        ])
        return df

    # TODO: there might be multiple types
    def extract_type(self, string):
        if "PREP." in string:
            return TypeModel.prep
        if "ADJ." in string:
            return TypeModel.adj
        if "ADV." in string:
            return TypeModel.adv
        if "V." in string:
            return TypeModel.v
        if "v." in string:
            return TypeModel.v
        if "n." in string:
            return TypeModel.n
        if "N." in string:
            return TypeModel.n

        return TypeModel.interj  # TODO: this is a placeholder

    def add_barron_to_database(self, only_iterate=False):
        """
        path: the csv file path input
        return: list_id, list_header
        """

        df = self.read_csv(self.path)

        added_vocab = set()

        for index, row in tqdm(df.iterrows()):
            vocab = str(row["Vocab"]).lower()
            vocab_id = "Barron:" + vocab
            edition = datetime.utcnow()
            list_id = self.list_id

            typ = self.extract_type(row["Type"])
            main_translation = row["VocabMeaning1"]
            other_translation = [
                row["Translate"], row["Google Translated"],
                row["VocabMeaning2"], row["VocabMeaning3"],
                row["VocabMeaning4"], row["VocabMeaning5"],
                row["VocabMeaning6"]
            ]

            other_translation = [
                i.replace("\n", "").replace(" ", "") for i in other_translation
                if not pd.isnull(i)
            ]

            main_sound = row["Pronounce1"]
            other_sound = None
            english_translation = row["EnglishTranslation"]
            confusing_words = None
            mem_tips = None
            example_sentences = [row["EnglishSentence"]]

            if only_iterate:
                added_vocab.add(vocab_id)
            else:
                vocab_db = VocabDB.get(vocab_id)
                if vocab_db == None:
                    vocab_db = VocabDB.add(
                        vocab_id=vocab_id,
                        edition=edition,
                        list_ids=[list_id],
                        vocab=vocab,
                        type=typ,
                        main_translation=main_translation,
                        other_translation=other_translation,
                        main_sound=main_sound,
                        other_sound=other_sound,
                        english_translation=english_translation,
                        confusing_words=confusing_words,
                        mem_tips=mem_tips,
                        example_sentences=example_sentences,
                    )
                    added_vocab.add(vocab_id)
                else:
                    current_app.logger.info("400|{} already exist".format(vocab_db))

        self.list_header["edition"] = datetime.utcnow()
        self.list_header["vocab_ids"] = added_vocab
