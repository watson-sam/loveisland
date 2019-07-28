import requests
import bs4 as bs
import pandas as pd
from loveisland.common.cli import base_parser


def get_df(args):
    req = requests.get(
        "https://en.wikipedia.org/wiki/Love_Island_(series_{})".format(str(args.season))
    )
    soup = bs.BeautifulSoup(req.content, "lxml")
    return pd.read_html(str(soup.find_all("table")[1]))[0]


def filter_dupe(df):
    return df[
        (df["Islander"] != "Alex Miller")
        & (df["Islander"] != "Charlie Williams")
        & (df["Islander"] != "Laura Crane")
        & (df["Islander"] != "Jack Fowler")
        & (df["Islander"] != "Josh Mair")
        & (df["Islander"] != "Ellie Jones")
        & (df["Islander"] != "Charlie Frederick")
    ]


def recode_cols(args, df):
    df["islander"] = df["Islander"].apply(lambda x: x.split(" ")[0].lower())
    df["arrived"] = df["Entered"].apply(lambda x: x.split(" ")[1])
    df["dumped"] = df["Status"].apply(
        lambda x: x.split("Day ")[1].replace(")", "") if x != "Participating" else 59
    )
    df["age"] = df["Age"]
    df["arrived"] = df["arrived"].astype(int)
    df["dumped"] = df["dumped"].astype(int)
    df["season"] = args.season
    return df[["islander", "arrived", "dumped", "age"]]


def to_dict(df):
    df = df.set_index("islander")
    print(df.to_dict(orient="index"))


def main(args):
    df = get_df(args)
    df = filter_dupe(df)
    df = recode_cols(args, df)
    to_dict(df)


if __name__ in "__main__":
    args = base_parser().parse_args()
    main(args)
