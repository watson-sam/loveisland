from loveisland.common.functions import Functions as F
from loveisland.common.constants import ISLANDERS, PUNC_LIST, EXTRA_STOPS, APPOS
from loveisland.common.cli import base_parser

from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import pandas as pd
import os
import re

import unicodedata
import spacy

nlp = spacy.load("en_core_web_lg")


class ProcessTweets(object):
    def __init__(self, args, d0, islanders):
        self.args = args
        self.d0 = d0
        self.df = None
        self.islanders = {
            k: v for k, v in islanders.items() if v["season"] == args.season
        }

    def read_data(self):
        """Import data"""
        path = os.path.join(
            self.args.bucket,
            "season_" + str(self.args.season),
            "raw_tweets",
            str(self.d0) + ".csv"
        )
        self.df = pd.read_csv(path)
        self.df["text"] = self.df["text"].astype(str)
        print("Running for", str(self.d0), "on", len(self.df), "tweets...")
        return self

    def get_user(self, col="url"):
        """From tweet url extract the username"""
        self.df["user"] = self.df[col].apply(lambda x: x.split("/")[3])
        return self

    def get_list(self, tweet):
        """Return list of islanders mentioned in a tweet"""
        return [e for e in self.islanders if re.findall("\\b" + e + "\\b", tweet.lower())]

    def get_islanders(self, col="text"):
        """Add column containing list of islanders mentioned"""
        self.df["islanders"] = self.df[col].apply(lambda x: self.get_list(x))
        return self

    def add_dummy_cols(self):
        """Create dummy variable columns for each islander"""
        for i, item in self.islanders.items():
            self.df[i] = self.df["islanders"].apply(
                lambda x: i if i in x else "nan"
            )
        return self

    def format_time(self):
        """Reformat the date column"""
        self.df["date"] = pd.to_datetime(self.df["date"])
        self.df["hour"] = self.df["date"].dt.hour
        self.df["dotw"] = self.df["date"].dt.strftime("%A")
        self.df["date"] = self.df["date"].dt.date
        return self

    def contains_pic(self, col="text"):
        """Tag if tweet contains a picture"""
        self.df["pic"] = self.df[col].apply(
            lambda x: "yes" if "pic.twitter.com" in x else "no"
        )
        return self

    @staticmethod
    def string_wise(text):
        """Apply some very simple stringwise logic to clean text"""
        # Make all text lowercase
        text = text.lower()
        # Remove all the punctuation in above list (quicker / more control that using re)
        for key, item in APPOS.items():
            text = text.replace(key, item)
        for punc in PUNC_LIST:
            text = text.replace(punc, " ")
        for punc in ["'", "`", "’"]:
            text = text.replace(punc, "")
        # Remove any leading and trailing whitespace
        return text.strip()

    @staticmethod
    def rm_numeric(text):
        return "".join(i for i in text if not i.isdigit())

    @staticmethod
    def remove_non_ascii(words):
        """Remove non-ASCII characters from list of tokenized words"""
        return (
            unicodedata.normalize("NFKD", words)
            .encode("ascii", "ignore")
            .decode("utf-8", "ignore")
        )

    @staticmethod
    def remove_li_ref(x):
        """Remove all references to love island out of each tweet
        (reducing noise for sentiment analysis)"""
        return x.replace("love island", "").replace("loveisland", "").replace("#", "")

    @staticmethod
    def spacy_inter(words):
        """Remove stopwords, punctuation and lemmatize words + tokenize"""
        return [w.lemma_ for w in nlp(words) if not w.is_stop and not w.is_punct]

    @staticmethod
    def drop_space(words):
        """Remove all spaces from text"""
        return [word.strip() for word in words]

    @staticmethod
    def remove_small_str(words, str_l=2):
        """Remove words with a length less than l"""
        return [w for w in words if len(w) > str_l]

    def wrapper(self, text):
        """Compile all preprocessing functions"""
        x = self.string_wise(text)
        x = self.rm_numeric(x)
        x = self.remove_non_ascii(x)
        x = self.remove_li_ref(x)
        x = self.spacy_inter(x)
        x = self.drop_space(x)
        x = self.remove_small_str(x)
        return x, " ".join(x)

    def apply_processing(self):
        """Populate tokens and processed text columns"""
        self.df["tokens"], self.df["processed_text"] = zip(
            *self.df["text"].apply(lambda x: self.wrapper(x))
        )
        return self

    def get_sentiment(self, col="processed_text"):
        """Find compound sentiment score"""
        sia = SIA()
        self.df["score"] = self.df[col].apply(lambda x: sia.polarity_scores(str(x)))
        self.df["score"] = self.df["score"].apply(lambda x: x["compound"])
        return self

    def weighted_sentiment(self):
        """Apply a weighting (n favourites) to each sentiment score"""
        self.df["weight_senti"] = self.df["favs"] * self.df["score"]
        return self

    def save(self):
        """Export data"""
        path = os.path.join(
            self.args.bucket,
            "season_" + str(self.args.season),
            "{}",
            str(self.d0) + ".csv"
        )
        self.df.to_csv(path.format("processed"), index=False)
        return self


def main(args):
    dates = F.get_date_list(args)
    for i in range(len(dates) - 1):
        d0, d1 = F.get_dates(i, dates)

        pt = ProcessTweets(args, d0, ISLANDERS)
        pt.read_data() \
            .get_user() \
            .get_islanders() \
            .add_dummy_cols() \
            .format_time() \
            .contains_pic() \
            .apply_processing() \
            .get_sentiment() \
            .weighted_sentiment() \
            .save()


def run():
    args = base_parser().parse_args()
    for sw in EXTRA_STOPS:
        nlp.vocab[sw].is_stop = True
    main(args)


if __name__ in "__main__":
    run()
