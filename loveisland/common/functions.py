import datetime as dt


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