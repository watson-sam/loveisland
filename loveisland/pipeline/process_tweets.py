from loveisland.common.functions import get_dates, get_date_list
from loveisland.common.constants import ISLANDERS
from loveisland.common.cli import base_parser

from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import pandas as pd
import os
import re


class ProcessTweets(object):
    def __init__(self, args, d0):
        self.args = args
        self.d0 = d0
        self.df = None
        self.agg_df = pd.DataFrame()

    def read_data(self):
        """Import data"""
        path = os.path.join(self.args.bucket, "raw_tweets", str(self.d0) + ".csv")
        self.df = pd.read_csv(path)
        return self

    @staticmethod
    def sort_text(x):
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

    def preprocess(self, col="text"):
        """Apply the brief first pre-processing steps"""
        self.df["processed"] = self.df[col].astype(str)
        self.df["processed"] = self.df["processed"].apply(lambda x: self.sort_text(x))
        return self

    def get_sentiment(self, col="processed"):
        """Find compound sentiment score"""
        sia = SIA()
        self.df["score"] = self.df[col].apply(lambda x: sia.polarity_scores(str(x)))
        self.df["score"] = self.df["score"].apply(lambda x: x["compound"])
        return self

    @staticmethod
    def get_list(tweet):
        """Return list of islanders mentioned in a tweet"""
        return [e for e in ISLANDERS if re.findall("\\b" + e + "\\b", tweet.lower())]

    def get_islanders(self, col="processed"):
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

    def islander_agg(self, islander):
        """Aggregate various metrics per islander/date"""
        AGG_JS = {
            "favs": "mean",
            "retwe": "mean",
            "score": "mean",
            "user": "nunique",
            "url": "count",
            "weight_senti": "mean",
        }
        RN_JS = {islander: "islander", "url": "n_tweets", "user": "n_users"}
        df = self.df[self.df[islander] == islander]
        df = df.groupby(islander).agg(AGG_JS).reset_index()
        df["date"] = self.d0
        return df.rename(columns=RN_JS)

    def aggregate_all(self):
        """Loop over all islanders, aggregating metrics"""
        for islander in ISLANDERS:
            agg = self.islander_agg(islander)
            self.agg_df = self.agg_df.append(agg).reset_index(drop=True)
        return self

    def format_time(self):
        """Reformat the date column"""
        self.df["date"] = pd.to_datetime(self.df["date"])
        self.df["hour"] = self.df["date"].dt.hour
        self.df["dotw"] = self.df["date"].dt.strftime("%A")
        self.df["date"] = self.df["date"].dt.date
        return self

    def contains_pic(self):
        """Tag if tweet contains a picture"""
        self.df["pic"] = self.df["processed"].apply(
            lambda x: "yes" if "pic.twitter.com" in x else "no"
        )
        return self

    def save(self):
        """Export data"""
        path = os.path.join(self.args.bucket, "{}", str(self.d0) + ".csv")
        self.df.to_csv(path.format("processed"), index=False)
        self.agg_df.to_csv(path.format("aggregated"), index=False)
        return self


def main(args):
    dates = get_date_list(args)
    for i in range(len(dates) - 1):
        d0, d1 = get_dates(i, dates)

        pt = ProcessTweets(args, d0)
        pt.read_data()\
            .get_user()\
            .preprocess()\
            .get_sentiment()\
            .get_islanders()\
            .add_dummy_cols()\
            .weighted_sentiment()\
            .aggregate_all()\
            .format_time()\
            .contains_pic()\
            .save()


def run():
    args = base_parser().parse_args()
    main(args)


if __name__ in "__main__":
    run()
