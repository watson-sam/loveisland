from argparse import ArgumentParser
import dateutil.parser
import datetime as dt


def base_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--bucket",
        type=str,
        default="/Users/samwatson/projects/loveisland/data/",
    )
    parser.add_argument(
        "-s",
        "--start_date",
        help="Start Date (YYYY-MM-DD)",
        type=dateutil.parser.isoparse,
        default=dt.datetime.strptime("2019-05-20", "%Y-%m-%d"),
    )
    parser.add_argument(
        "-e",
        "--end_date",
        help="End Date (YYYY-MM-DD)",
        type=dateutil.parser.isoparse,
        default=(dt.datetime.now() + dt.timedelta(days=1)),
    )
    parser.add_argument(
        "--yesterday",
        help="If to scrape tweets only from yesterday -> today",
        action="store_true",
    )
    parser.add_argument(
        "--season",
        help="Which season are we concentrating on?",
        type=int,
        default=4,
    )
    return parser
