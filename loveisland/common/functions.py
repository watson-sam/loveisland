import datetime as dt
import pandas as pd
import glob
from loveisland.common.constants import ISLANDERS


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


def get_dates(i, dates):
    return dates[i], dates[i + 1]


def import_all(path="../data/processed/"):
    df_list = [pd.read_csv(f, low_memory=False) for f in glob.glob(path + "*.csv")]
    df = pd.concat(df_list, ignore_index=True, sort=True)
    df["date"] = pd.to_datetime(df["date"])
    return df


def get_palette():
    palette = {}
    for key, item in ISLANDERS.items():
        palette[key] = item["col"]
    return palette


def get_islanders(when="original"):
    islanders = []
    for key, item in ISLANDERS.items():
        if when == "original" and item["arrived"] == 1:
            islanders.append(key)
        elif when == "casa_amor" and item["arrived"] == 26:
            islanders.append(key)
    return islanders


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


def get_islander_df():
    df = pd.DataFrame.from_dict(ISLANDERS, orient="index")
    df.index.name = "islander"
    return df.reset_index()
