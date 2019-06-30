import gensim
from loveisland.common.functions import import_all
from collections import Counter
import seaborn as sns
from matplotlib import pyplot as plt

import pandas as pd


def str_to_list(string):
    return (
        string.replace("[", "")
        .replace("]", "")
        .replace("'", "")
        .replace(" ", "")
        .split(",")
    )


def ngrams(df, col="processed_text"):
    ngram = gensim.models.Phrases(df[col])
    df[col] = df[col].apply(lambda x: ngram[x])
    return df


def get_tokens(df, col="processed_text"):
    return [item for sublist in df[col].to_list() for item in sublist]


def get_df(temp, col, date):
    df = get_counts(get_tokens(temp, col))
    df["n_tweets"] = temp.url.nunique()
    df["date"] = date
    df["percent"] = df["count"] / sum(df["count"])
    return df


def tokens_by_dt(df, dt_col="date", col="processed_text"):
    df_list = []
    for date in df[dt_col].unique():
        temp = df[df[dt_col] == date]
        df_list.append(get_df(temp, col, date))
    return pd.concat(df_list, ignore_index=True)


def get_counts(tokens):
    counts = Counter(tokens)
    counts = pd.DataFrame.from_dict(counts, orient="index", columns=["count"])
    counts.index.name = "token"
    return counts.reset_index().sort_values("count", ascending=False)


if __name__ in "__main__":
    # df = import_all()
    df = pd.read_csv(
        "/Users/samwatson/projects/loveisland/data/processed/2019-05-20.csv"
    )

    for i in range(20, 30):
        df = df.append(
            pd.read_csv(
                "/Users/samwatson/projects/loveisland/data/processed/2019-05-{}.csv".format(
                    i
                )
            ),
            sort=True,
        )

    df["processed_text"] = df["processed_text"].apply(lambda x: str_to_list(x))
    df = ngrams(df)
    df = ngrams(df)
    all_tokens = get_tokens(df)
    counts = get_counts(all_tokens)

    fig = plt.figure(figsize=(15, 5))
    ax1 = fig.add_subplot(111)
    sns.barplot("token", "count", data=counts.head(20), color="Red", ax=ax1)
    plt.xticks(rotation=50)
    plt.show()

    # js = tokens_by_dt(df)
    # js = js.sort_values("count", ascending=False).groupby("date").head(10)
    #
    # order = js.token.unique()
    # g = sns.FacetGrid(
    #     col="date", col_wrap=1, data=js, height=3, aspect=3, sharex=False, sharey=False
    # )
    # g.map(sns.barplot, "token", "count", order=order, color="Red")
    # g.set_xticklabels(rotation=60)
    # plt.show()
