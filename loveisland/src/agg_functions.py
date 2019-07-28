import pandas as pd
import numpy as np
import os

from loveisland.common.cli import base_parser
from loveisland.common.constants import ISLANDERS
from loveisland.common.functions import Functions as F


class AggregateData:
    def __init__(self, args):
        self.args = args
        self.df = F.import_all(
            os.path.join(args.bucket, "season_" + str(args.season), "processed/")
        )

        self.inc_islander()

        self.agg_df = pd.DataFrame()
        self.islanders = {
            k: v for k, v in ISLANDERS.items() if v["season"] == args.season
        }

    def inc_islander(self, col="islanders"):
        self.df[col] = self.df[col].apply(lambda x: F.str_to_list(x))
        self.df["inc_islander"] = self.df[col].apply(lambda x: len(x))
        self.df["inc_islander"] = np.where(self.df["inc_islander"] < 1, "No", "Yes")
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
        df = df[df["score"] != 0]
        if len(df) > 0:
            return (
                df.groupby([islander, "date"])
                .agg(AGG_JS)
                .reset_index()
                .rename(columns=RN_JS)
            )
        return pd.DataFrame()

    def aggregate_all(self):
        """Loop over all islanders, aggregating metrics"""
        for islander in self.islanders:
            agg = self.islander_agg(islander)
            self.agg_df = self.agg_df.append(agg, sort=True)
        self.agg_df = self.agg_df.reset_index(drop=True)
        return self

    def add_cols(self):
        self.agg_df["total_favs"] = self.agg_df["favs"] * self.agg_df["n_tweets"]
        self.agg_df["total_retwe"] = self.agg_df["retwe"] * self.agg_df["n_tweets"]
        self.agg_df = self.agg_df.merge(
            F.get_islander_df(self.args.season), on="islander", how="left"
        )

        self.agg_df["n_days"] = self.agg_df["dumped"] - self.agg_df["arrived"]
        self.agg_df["n_days"] = np.where(
            self.agg_df["dumped"] == 0,
            60 - self.agg_df["arrived"],
            self.agg_df["n_days"],
        )
        return self

    def do_aggregate(self, min_tweets=100):
        self.aggregate_all()
        self.agg_df = self.agg_df[
            (self.agg_df["n_tweets"] >= min_tweets)
            & (self.agg_df["islander"].isin(self.islanders))
        ]
        self.add_cols()
        return self

    def save(self):
        path = os.path.join(self.args.bucket, "season_" + str(self.args.season), "{}")
        self.df.to_csv(path.format("full_df.csv"), index=False)
        self.agg_df.to_csv(path.format("agg_df.csv"), index=False)
        return self


def run(args):
    ag = AggregateData(args)
    ag.do_aggregate().save()


def main():
    args = base_parser().parse_args()
    run(args)


if __name__ in "__main__":
    main()
