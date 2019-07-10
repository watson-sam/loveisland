from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import GridSearchCV

# import gensim
import seaborn as sns
from matplotlib import pyplot as plt
import pickle

import pandas as pd

N_TOPICS = [10, 15, 20, 25, 30]
L_DECAY = [0.3, 0.5, 0.7, 0.9]
SEARCH_PARAM = {"n_components": N_TOPICS, "learning_decay": L_DECAY}


def import_data(path):
    df = pd.read_csv(path)
    df["processed_text"] = df["processed_text"].astype(str)
    df["tokens"] = df["processed_text"].apply(lambda x: x.split(" "))
    return df


def vectorize(df, col="processed_text"):
    """Get feature names + back of words"""
    vectorizer = CountVectorizer()
    A = vectorizer.fit_transform(df[col])
    return A, vectorizer.get_feature_names()


# def w2v_mod(df, col="tokens"):
#     """Create word2vec model as list of documents"""
#     return gensim.models.Word2Vec(df[col], min_count=1)


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
    df = []
    for i in L_DECAY:
        ll_res = get_ll(model.cv_results_, i)
        for index, (ll, t) in enumerate(zip(ll_res, N_TOPICS)):
            df.append(
                {"Learning decay": i, "Log Likelyhood Score": ll, "Number of Topics": t}
            )
    return pd.DataFrame(df)


def display_topics(model, feature_names, n_words):
    for topic_idx, topic in enumerate(model.components_):
        print(
            "Topic",
            topic_idx,
            ":",
            [feature_names[i] for i in topic.argsort()[: -(n_words + 1) : -1]],
        )


dt = "2019-06-07"
df = import_data(
    "/Users/samwatson/projects/loveisland/data/processed/{}.csv".format(dt)
)
# df = df[:5000]
A, bag_of_words = vectorize(df)
# w2v_model = w2v_mod(df)

model = setup_grid()
model.fit(A)
best_mod = model.best_estimator_

# Model Parameters
print("Best Model's Params: ", model.best_params_)
print("Best Log Likelihood Score: ", model.best_score_)
print("Model Perplexity: ", best_mod.perplexity(A))

ll_df = fill_df(model)


# Show graph
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111)
sns.lineplot(
    "Number of Topics", "Log Likelyhood Score", data=ll_df, ax=ax, hue="Learning decay"
)
plt.title("Choosing Optimal LDA Model")
plt.legend(title="Learning decay", loc="best")
plt.show()


filename = "/Users/samwatson/projects/loveisland/data/models/{}.csv".format(dt)
pickle.dump(best_mod, open(filename, "wb"))
loaded_model = pickle.load(open(filename, "rb"))

no_top_words = 10
display_topics(loaded_model, bag_of_words, no_top_words)


# import pyLDAvis.sklearn
#
# pyLDAvis.enable_notebook()
# panel = pyLDAvis.sklearn.prepare(lda_model, A, vectorizer, mds='tsne')
# panel
