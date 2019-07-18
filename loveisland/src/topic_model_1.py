from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import GridSearchCV

import os
import seaborn as sns
from matplotlib import pyplot as plt
import pickle
import pandas as pd

from loveisland.common.functions import get_dates, get_date_list
from loveisland.common.cli import base_parser

N_TOPICS = [10, 15, 20, 25, 30]
L_DECAY = [0.3, 0.5, 0.7, 0.9]
SEARCH_PARAM = {"n_components": N_TOPICS, "learning_decay": L_DECAY}


def import_data(args, dt):
    """Import and format data"""
    df = pd.read_csv(
        os.path.join(args.bucket, "processed", str(dt) + ".csv"), low_memory=False
    )
    df["processed_text"] = df["processed_text"].astype(str)
    df["tokens"] = df["processed_text"].apply(lambda x: x.split(" "))
    return df


def vectorize(df, col="processed_text"):
    """Get feature names + back of words"""
    vectorizer = CountVectorizer()
    A = vectorizer.fit_transform(df[col])
    return A, vectorizer


def setup_grid():
    # Set up class
    lda = LatentDirichletAllocation()
    # Initialize grid search
    return GridSearchCV(lda, param_grid=SEARCH_PARAM, cv=5)


def get_ll(m, learning_decay):
    return [
        m["mean_test_score"][i]
        for i in range(len(m["mean_fit_time"]))
        if m["params"][i]["learning_decay"] == learning_decay
    ]


def fill_df(model):
    df = list()
    for i in L_DECAY:
        ll_res = get_ll(model.cv_results_, i)
        for index, (ll, t) in enumerate(zip(ll_res, N_TOPICS)):
            df.append(
                {"Learning decay": i, "Log Likelyhood Score": ll, "Number of Topics": t}
            )
    return pd.DataFrame(df)


def ll_graph(mod):
    ll_df = fill_df(mod)
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111)
    sns.lineplot(
        "Number of Topics",
        "Log Likelyhood Score",
        data=ll_df,
        ax=ax,
        hue="Learning decay",
    )
    plt.title("Choosing Optimal LDA Model")
    plt.legend(title="Learning decay", loc="best")
    plt.show()


def display_topics(mod, feature_names, n_words):
    for topic_idx, topic in enumerate(mod.components_):
        print(
            "Topic",
            topic_idx,
            ":",
            [feature_names[i] for i in topic.argsort()[: -(n_words + 1) : -1]],
        )


def save_aspects(args, dt, mod, vectorizer):
    path = os.path.join(args.bucket, "{}", str(dt) + ".pkl")
    pickle.dump(mod, open(path.format("models"), "wb"))
    pickle.dump(vectorizer.vocabulary_, open(path.format("vocab"), "wb"))


def save_best_params(args, dt, grid):
    path = os.path.join(args.bucket, "best_param.pkl")
    if os.path.exists(path):
        with open(path, "rb") as f:
            js = pickle.load(f)
    else:
        js = dict()

    js[str(dt)] = grid.best_params_

    pickle.dump(js, open(path, "wb"))


def main(args):
    dates = get_date_list(args)
    for i in range(len(dates) - 1):
        d0, d1 = get_dates(i, dates)
        print("Running for", d0)

        df = import_data(args, d0)
        A, vectorizer = vectorize(df)
        # bag_of_words = vectorizer.get_feature_names()

        grid = setup_grid()
        grid.fit(A)

        best_mod = grid.best_estimator_

        save_aspects(args, d0, best_mod, vectorizer)
        save_best_params(args, d0, grid)

        print("Topics for", d0, "found and saved")

        # print("Best Model's Parameters:", grid.best_params_)
        # print("Best Log Likelihood Score:", grid.best_score_)
        # print("Model Perplexity:", best_mod.perplexity(A))
        #
        # ll_graph(best_mod)
        #
        # no_top_words = 10
        # display_topics(best_mod, bag_of_words, no_top_words)


def run():
    args = base_parser().parse_args()
    main(args)


if __name__ in "__main__":
    run()


# import pyLDAvis.sklearn
#
# pyLDAvis.enable_notebook()
# panel = pyLDAvis.sklearn.prepare(lda_model, A, vectorizer, mds='tsne')
# panel
#
# loaded_model = pickle.load(open(filename, "rb"))

