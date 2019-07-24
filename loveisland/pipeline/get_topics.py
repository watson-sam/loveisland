from loveisland.common.functions import Functions as F

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import GridSearchCV

import os
import pickle
import pandas as pd
import pyLDAvis.sklearn

from argparse import ArgumentParser
import dateutil.parser
import datetime as dt

N_TOPICS = [10, 15, 20, 25, 30]
L_DECAY = [0.3, 0.5, 0.7, 0.9]
SEARCH_PARAM = {"n_components": N_TOPICS, "learning_decay": L_DECAY}


class GetTopics(object):
    def __init__(self, args, d0):
        self.args = args
        self.d0 = d0
        self.df = None
        self.A = None
        self.vectorizer = None
        self.mod = None

    def import_data(self):
        """Import and format data"""
        self.df = pd.read_csv(
            os.path.join(
                self.args.bucket,
                "season_" + str(self.args.season),
                "processed",
                str(self.d0) + ".csv",
            ),
            low_memory=False,
        )
        self.df["processed_text"] = self.df["processed_text"].astype(str)
        self.df["tokens"] = self.df["processed_text"].apply(lambda x: x.split(" "))
        return self

    def vectorize(self, col="processed_text"):
        """Get feature names + back of words"""
        self.vectorizer = CountVectorizer()
        self.A = self.vectorizer.fit_transform(self.df[col])
        return self

    def save_best_params(self, grid):
        path = os.path.join(
            self.args.bucket, "season_" + str(self.args.season), "best_param.pkl"
        )

        if os.path.exists(path):
            with open(path, "rb") as f:
                js = pickle.load(f)
        else:
            js = dict()

        js[str(self.d0)] = grid.best_params_
        pickle.dump(js, open(path, "wb"))

    @staticmethod
    def setup_grid():
        # Set up class
        lda = LatentDirichletAllocation()
        # Initialize grid search
        return GridSearchCV(lda, param_grid=SEARCH_PARAM, cv=5)

    def get_best(self):
        grid = self.setup_grid()
        grid.fit(self.A)
        self.mod = grid.best_estimator_
        self.save_best_params(grid)
        return self

    def save_aspects(self):
        path = os.path.join(
            self.args.bucket,
            "season_" + str(self.args.season),
            "{}",
            str(self.d0) + ".pkl",
        )
        pickle.dump(self.mod, open(path.format("models"), "wb"))
        pickle.dump(self.vectorizer.vocabulary_, open(path.format("vocab"), "wb"))
        return self

    def get_visual(self):
        p = pyLDAvis.sklearn.prepare(self.mod, self.A, self.vectorizer)
        pyLDAvis.save_html(
            p,
            os.path.join(
                self.args.bucket,
                "season_" + str(self.args.season),
                "pylda_htmls",
                str(self.d0) + ".html",
            ),
        )
        return p


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
        default=dt.datetime.strptime("2019-07-02", "%Y-%m-%d"),
    )
    parser.add_argument(
        "-e",
        "--end_date",
        help="End Date (YYYY-MM-DD)",
        type=dateutil.parser.isoparse,
        default=dt.datetime.strptime("2019-07-03", "%Y-%m-%d"),
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
        default=5,
    )
    return parser


def main(args):
    dates = F.get_date_list(args)
    for i in range(len(dates) - 1):
        d0, d1 = F.get_dates(i, dates)

        print("Running for", d0)
        gt = GetTopics(args, d0)
        gt.import_data().vectorize().get_best().save_aspects().get_visual()
        print("Topics for", d0, "found and saved")


def run():
    args = base_parser().parse_args()
    main(args)


if __name__ in "__main__":
    run()
