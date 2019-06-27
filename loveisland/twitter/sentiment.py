from loveisland.common.functions import get_dates, get_date_list
from loveisland.common.cli import base_parser

from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import pandas as pd
import os

pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 500)
pd.set_option("display.width", 1000)


def preprocess(df, col="text"):
    df[col] = df[col].str.lower()
    df[col] = df[col].str.replace("loveisland", "").str.replace("love island", "").replace("#", "")
    return df



def sentiment_scores(df):
    sia = SIA()
    df["score"] = df["text"].apply(lambda x: sia.polarity_scores(str(x)))
    # df["score"] = df["score"].apply(lambda x: x["pos"] - x["neg"])
    # df = df[df["score"] != 0]
    df["score2"] = df["score"].apply(lambda x: x["compound"])
    print("Completed " + str(len(df)) + " Sentiment scores")
    return df


def main(args):
    dates = get_date_list(args)
    # for i in range(len(dates)-1):
    for i in range(10):
        d0, d1 = get_dates(i, dates)

        path = os.path.join(args.bucket, str(d0) + ".csv")
        df = pd.read_csv(path)
        df = preprocess(df)
        print(sentiment_scores(df).head())


def run():
    args = base_parser().parse_args()
    main(args)


if __name__ in "__main__":
    run()