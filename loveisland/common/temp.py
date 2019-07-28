class AggAgg:
    def __init__(self, args):
        self.args = args
        self.df = pd.read_csv(
            os.path.join(args.bucket, "season_" + str(args.season), "agg_df.csv")
        )

    @staticmethod
    def date_to_n_lookup(df):
        n_list = list(range(1, df["dumped"].max() + 1))
        d_list = [(df["date"].min() + dt.timedelta(days=n)).date() for n in n_list]
        return pd.DataFrame.from_dict({"dumped": n_list, "dumped_d": d_list})

    def create_dummy(self):
        self.df["male"] = np.where(self.df["sex"] == "male", 1, 0)
        return self

    def create_days(self):
        self.df["n_days"] = np.where(
            self.df["dumped"] == 0,
            60 - self.df["arrived"],
            self.df["dumped"] - self.df["arrived"],
        )
        return self

    def start_end(self):
        if self.args.season == 4:
            sd, ed = "2018-06-04", "2018-07-30"
        else:
            sd, ed = "2019-06-03", "2019-07-30"

        self.df = self.df[(sd <= self.df["date"]) & (self.df["date"] < ed)].reset_index(
            drop=True
        )
        return self

    def islander_agg(self):
        self.df["date"] = pd.to_datetime(self.df["date"])
        self.start_end()
        self.df = self.df.merge(self.date_to_n_lookup(self.df), on="dumped", how="left")
        self.df["dumped_d"] = pd.to_datetime(self.df["dumped_d"])
        self.df = self.df[
            (self.df["date"] <= self.df["dumped_d"]) | (self.df["dumped"] == 0)
        ].reset_index(drop=True)

        self.df = (
            self.df.groupby(["islander", "date"])
            .agg({"n_tweets": "sum", "score": "mean"})
            .reset_index()
        )
        self.df["n_tweets_perc"] = self.df.groupby("date")["n_tweets"].apply(
            lambda x: x * 100 / sum(x)
        )
        self.df = (
            df.groupby("islander")
            .agg({"n_tweets": "sum", "score": "mean", "n_tweets_perc": "mean"})
            .reset_index()
        )

        self.df = self.df.merge(
            F.get_islander_df(self.args.season), on="islander", how="left"
        )
        return self


def fit_mod(df, dep_col="n_days", ind_cols=["n_tweets_perc", "score", "male"]):
    reg = linear_model.LinearRegression(normalize=True)
    reg.fit(df[ind_cols], df[dep_col])
    return reg


def apply_mod(df, req):
    df["pred"] = df.apply(
        lambda row: reg.predict([[row["n_tweets_perc"], row["score"], row["male"]]])[0],
        axis=1,
    )
    df["diff"] = df["n_days"] - df["pred"]
    df["b_o_w"] = np.where(df["diff"] < 0, "worse", "better")
    return df
