import datetime as dt
import pandas as pd
import glob
from loveisland.common.constants import ISLANDERS_4, ISLANDERS_5


def get_islanders_s(season=5):
    if season == 4:
        return ISLANDERS_4
    else:
        return ISLANDERS_5


class Functions(object):
    @staticmethod
    def get_date_list(args):
        if args.yesterday:
            sd = dt.datetime.now() - dt.timedelta(days=1)
            ed = dt.datetime.now()
        else:
            sd = args.start_date
            ed = args.end_date

        delta = (ed - sd).days

        dates = []
        for i in range(delta + 1):
            dates.append((sd + dt.timedelta(days=i)).date())
        return dates

    @staticmethod
    def get_dates(i, dates):
        return dates[i], dates[i + 1]

    @staticmethod
    def import_all(path="../data/season_5/processed/"):
        df_list = [pd.read_csv(f, low_memory=False) for f in glob.glob(path + "*.csv")]
        df = pd.concat(df_list, ignore_index=True, sort=True)
        df["date"] = pd.to_datetime(df["date"])
        return df

    @staticmethod
    def get_palette(season=5):
        palette = {}
        for key, item in get_islanders_s(season).items():
            palette[key] = item["col"]
        return palette

    @staticmethod
    def get_islanders(when="original", season=5):
        islanders = []
        for key, item in get_islanders_s(season).items():
            if item["season"] == season:
                if when == "original" and item["arrived"] == 1:
                    islanders.append(key)
                elif when == "casa_amor" and item["arrived"] == 26:
                    islanders.append(key)
        return islanders

    @staticmethod
    def str_to_list(string):
        string = str(string)
        return list(
            filter(
                None,
                (
                    string.replace("[", "")
                    .replace("]", "")
                    .replace("'", "")
                    .strip()
                    .split(",")
                ),
            )
        )

    def col_to_list(self, df, col):
        df[col] = df[col].apply(lambda x: self.str_to_list(x))
        return df

    @staticmethod
    def get_islander_df(season=5):
        df = pd.DataFrame.from_dict(get_islanders_s(season), orient="index")
        df = df[df["season"] == season]
        df.index.name = "islander"
        return df.reset_index()

    @staticmethod
    def get_islanders_s(season=5):
        if season == 4:
            return ISLANDERS_4
        else:
            return ISLANDERS_5
