import datetime as dt


def get_date_list(args):
    if args.yesterday:
        sd = (dt.datetime.now() - dt.timedelta(days=1)).date()
    else:
        sd = args.start_date.date()

    delta = (args.end_date - sd).days

    dates = []
    for i in range(delta + 1):
        dates.append(sd + dt.timedelta(days=i))
    return dates


def get_dates(i, dates):
    return dates[i], dates[i + 1]