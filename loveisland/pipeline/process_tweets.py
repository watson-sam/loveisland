from loveisland.common.functions import get_dates, get_date_list
from loveisland.common.constants import ISLANDERS, PUNC_LIST, EXTRA_STOPS
from loveisland.common.cli import base_parser

from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import pandas as pd
import os
import re

import unicodedata
import spacy

nlp = spacy.load("en_core_web_lg")


class ProcessTweets(object):
    def __init__(self, args, d0):
        self.args = args
        self.d0 = d0
        self.df = None

    def read_data(self):
        """Import data"""
        path = os.path.join(self.args.bucket, "raw_tweets", str(self.d0) + ".csv")
        self.df = pd.read_csv(path)
        print(len(self.df))
        return self

    @staticmethod
    def remove_li_ref(x):
        """Remove all references to love island out of each tweet
        (reducing noise for sentiment analysis)"""
        return (
            x.replace("Love island", "")
            .replace("loveisland", "")
            .replace("LoveIsland", "")
            .replace("Love Island", "")
            .replace("love island", "")
            .replace("#", "")
        )

    def get_user(self, col="url"):
        """From tweet url extract the username"""
        self.df["user"] = self.df[col].apply(lambda x: x.split("/")[3])
        return self

    def initial_preprocess(self, col="text", rtn_col="processed_text"):
        """Apply the brief first pre-processing steps"""
        self.df[rtn_col] = self.df[col].astype(str)
        self.df[rtn_col] = self.df[rtn_col].apply(lambda x: self.remove_li_ref(x))
        return self

    def get_sentiment(self, col="processed_text"):
        """Find compound sentiment score"""
        sia = SIA()
        self.df["score"] = self.df[col].apply(lambda x: sia.polarity_scores(str(x)))
        self.df["score"] = self.df["score"].apply(lambda x: x["compound"])
        return self

    @staticmethod
    def get_list(tweet):
        """Return list of islanders mentioned in a tweet"""
        return [e for e in ISLANDERS if re.findall("\\b" + e + "\\b", tweet.lower())]

    def get_islanders(self, col="processed_text"):
        """Add column containing list of islanders mentioned"""
        self.df["islanders"] = self.df[col].apply(lambda x: self.get_list(x))
        return self

    def add_dummy_cols(self):
        """Create dummy variable columns for each islander"""
        for pers in ISLANDERS:
            self.df[pers] = self.df["islanders"].apply(
                lambda x: pers if pers in x else "nan"
            )
        return self

    def weighted_sentiment(self):
        """Apply a weighting (n favourites) to each sentiment score"""
        self.df["weight_senti"] = self.df["favs"] * self.df["score"]
        return self

    def format_time(self):
        """Reformat the date column"""
        self.df["date"] = pd.to_datetime(self.df["date"])
        self.df["hour"] = self.df["date"].dt.hour
        self.df["dotw"] = self.df["date"].dt.strftime("%A")
        self.df["date"] = self.df["date"].dt.date
        return self

    def contains_pic(self, col="processed_text"):
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
        for punc in PUNC_LIST:
            text = text.replace(punc, " ")
        for punc in ["'", "`", "’"]:
            text = text.replace(punc, "")
        # Remove any leading and trailing whitespace
        return text.strip()

    @staticmethod
    def remove_non_ascii(words):
        """Remove non-ASCII characters from list of tokenized words"""
        return (
            unicodedata.normalize("NFKD", words)
            .encode("ascii", "ignore")
            .decode("utf-8", "ignore")
        )

    @staticmethod
    def drop_space(words):
        """Remove all spaces from text"""
        return [word.replace(" ", "") for word in words]

    @staticmethod
    def spacy_inter(words):
        """Remove stopwords, punctuation and lemmatize words + tokenize"""
        return [
            word.lemma_ for word in nlp(words) if not word.is_stop and not word.is_punct
        ]

    @staticmethod
    def remove_small_str(words, l=2):
        """Remove words with a length less than l"""
        return [word.strip() for word in words if len(word) > l]

    def wrapper(self, text):
        x = self.string_wise(text)
        x = self.remove_non_ascii(x)
        x = self.remove_li_ref(x)
        x = self.spacy_inter(x)
        x = self.drop_space(x)
        return self.remove_small_str(x)

    def apply_processing(self, col="processed_text"):
        self.df[col] = self.df[col].apply(lambda x: self.wrapper(x))
        return self

    def save(self):
        """Export data"""
        path = os.path.join(self.args.bucket, "{}", str(self.d0) + ".csv")
        self.df.to_csv(path.format("processed"), index=False)
        return self


def main(args):
    dates = get_date_list(args)
    for i in range(len(dates) - 1):
        d0, d1 = get_dates(i, dates)

        pt = ProcessTweets(args, d0)
        pt.read_data()\
            .get_user()\
            .initial_preprocess()\
            .get_sentiment()\
            .get_islanders()\
            .add_dummy_cols()\
            .weighted_sentiment()\
            .format_time()\
            .contains_pic()\
            .apply_processing()\
            .save()


def run():
    args = base_parser().parse_args()

    for sw in EXTRA_STOPS:
        nlp.vocab[sw].is_stop = True
    main(args)


if __name__ in "__main__":
    run()
