class GetInputs:
    def __init__(self, args, dates):
        self.args = args
        self.dates = dates
        self.stored = {}
        self.to_plot = None

    def import_aspects(self, dt):
        """Import model + vocabulary for a given date"""
        path = os.path.join(
            self.args.bucket, "season_" + str(self.args.season), "{}", str(dt) + ".pkl"
        )
        return (
            pickle.load(open(path.format("models"), "rb")),
            pickle.load(open(path.format("vocab"), "rb")),
        )

    def setup_aspects(self, dt, col="processed_text"):
        """Set up all the aspects from the topic modelling we need downstream"""
        gt = GetTopics(self.args, dt)
        gt.import_data()

        mod, vocab = self.import_aspects(dt)

        vectorizer = CountVectorizer(vocabulary=vocab)
        vectorizer._validate_vocabulary()
        A = vectorizer.fit_transform(gt.df[col])
        return gt.df, mod, vectorizer, A, vectorizer.get_feature_names()

    @staticmethod
    def topic_probs(doc_tops, df):
        """Assign the 'most likely' topic for every tweet in the corpus and the probability
        of that tweet being in that topic compared with any others"""

        # df[df["text"].str.contains("pic.twitter.com") == False]
        for_df = []
        for i in range(len(doc_tops)):
            js = {str(j): float(doc_tops[i][j]) for j in range(len(doc_tops[i]))}
            js["processed_text"] = df["processed_text"][i]
            for_df.append(js)

        for_df = pd.melt(
            pd.DataFrame(for_df), id_vars=["processed_text"], var_name="topic"
        )
        for_df["val_max"] = for_df.groupby(["processed_text"])["value"].transform(max)
        for_df = (
            for_df[for_df["value"] == for_df["val_max"]]
            .drop(columns="val_max")
            .reset_index(drop=True)
        )
        df = df.merge(for_df, on="processed_text", how="left").drop_duplicates(
            ["processed_text"]
        )
        df["text"] = df["text"].astype(str)
        return df[~df["text"].str.contains("pic.twitter.com")].reset_index(drop=True)

    def fill(self, dt, df, mod, vectorizer, A, bag_of_words):
        """Fill a dictionary with all the gathered elements for a given date"""
        self.stored[dt] = {
            "df": df,
            "mod": mod,
            "vectorizer": vectorizer,
            "A": A,
            "bag_of_words": bag_of_words,
            "n_tweets": df.url.nunique(),
            "perplexity": mod.perplexity(A),
        }
        return self

    def wrapper(self, dt):
        """Bring all methods together for a given date"""
        df, mod, vectorizer, A, bag_of_words = self.setup_aspects(dt)
        doc_tops = mod.transform(A)
        df = self.topic_probs(doc_tops, df)

        self.fill(dt, df, mod, vectorizer, A, bag_of_words)
        return self

    def get_all(self):
        """Loop over all dates we want to include in analysis"""
        for dt in self.dates:
            self.wrapper(dt)
        return self

    @staticmethod
    def dict_to_df(_dict, col="date"):
        """Transform a dictionary to pandas df"""
        df = pd.DataFrame.from_dict(_dict, orient="index")
        df.index.name = col
        return df.reset_index(drop=False)

    def prep_for_plot(self):
        """Extract relevant columns for a plot"""
        self.to_plot = {
            k: {"n_tweets": v["n_tweets"], "perplexity": v["perplexity"]}
            for k, v in self.stored.items()
        }
        self.to_plot = self.dict_to_df(self.to_plot)
        return self

    def add_params(self):
        """Augment df with parameters used in the topic modelling"""
        params = pickle.load(
            open(
                os.path.join(
                    args.bucket, "season_" + str(args.season), "best_param.pkl"
                ),
                "rb",
            )
        )
        params = self.dict_to_df(params)
        self.to_plot = self.to_plot.merge(params, on="date", how="left")
        self.to_plot["date"] = self.to_plot["date"].astype(str)
        return self
