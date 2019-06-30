import datetime as dt
import pandas as pd
import glob


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
    df_list = [pd.read_csv(f) for f in glob.glob(path + "*.csv")]
    df = pd.concat(df_list, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"])
    return df