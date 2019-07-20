from loveisland.pipeline.got3.manager import TweetCriteria, TweetManager
from loveisland.common.functions import Functions as F
from loveisland.common.cli import base_parser

import pandas as pd
import os


class GetTweets(object):
    def __init__(self, args, d0, d1):
        self.args = args
        self.d0 = d0
        self.d1 = d1
        self.all_tweets = None
        self.all_info = []

    def get_tweets(self):
        self.all_tweets = TweetManager.getTweets(
            TweetCriteria()
            .setQuerySearch("loveisland")
            .setSince(str(self.d0))
            .setUntil(str(self.d1))
            .setLang("en")
        )
        return self

    @staticmethod
    def get_info(tweet):
        return {
            "text": tweet.text,
            "url": tweet.permalink,
            "favs": tweet.favorites,
            "date": tweet.date,
            "retwe": tweet.retweets,
        }

    def fill_list(self):
        for tweet in self.all_tweets:
            self.all_info.append(self.get_info(tweet))
        return self

    def save(self):
        path = os.path.join(
            self.args.bucket,
            "season_" + str(self.args.season),
            "raw_tweets",
            str(self.d0) + ".csv",
        )
        pd.DataFrame(self.all_info).to_csv(path, index=False)
        return self


def main(args):
    dates = F.get_date_list(args)
    for i in range(len(dates) - 1):
        d0, d1 = F.get_dates(i, dates)
        print("Running for", d0)
        gt = GetTweets(args, d0, d1)
        gt.get_tweets().fill_list().save()
        print("Done", d0, "found", len(gt.all_info), "tweets")


def run():
    args = base_parser().parse_args()
    main(args)


if __name__ in "__main__":
    run()
