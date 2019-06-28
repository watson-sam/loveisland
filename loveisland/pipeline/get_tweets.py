from loveisland.pipeline.got3.manager import TweetCriteria, TweetManager
from loveisland.common.functions import get_dates, get_date_list
from loveisland.common.cli import base_parser

import pandas as pd
import os


def get_tweets(d0, d1):
    tweetCriteria = (
        TweetCriteria()
        .setQuerySearch("loveisland")
        .setSince(str(d0))
        .setUntil(str(d1))
        # .setMaxTweets(100)
        .setLang("en")
    )
    return TweetManager.getTweets(tweetCriteria)


def fill_dict(tweet):
    return {
        "text": tweet.text,
        "url": tweet.permalink,
        "favs": tweet.favorites,
        "date": tweet.date,
        "retwe": tweet.retweets,
    }


def fill_list(info, tweet):
    info.append(fill_dict(tweet))


def get_info(tweets):
    info = []
    for tweet in tweets:
        fill_list(info, tweet)
    return info


def save(args, info, d0):
    path = os.path.join(args.bucket, "raw_tweets", str(d0) + ".csv")
    pd.DataFrame(info).to_csv(path, index=False)


def main(args):
    dates = get_date_list(args)
    for i in range(len(dates) - 1):
        d0, d1 = get_dates(i, dates)
        print(d0)
        tweets = get_tweets(d0, d1)
        info = get_info(tweets)
        save(args, info, d0)
        print(d0, len(info))


def run():
    args = base_parser().parse_args()
    main(args)


if __name__ in "__main__":
    run()
