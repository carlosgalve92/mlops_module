import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted


class mb_clean_cat_number(BaseEstimator, TransformerMixin):
    """ """

    def __init__(
        self,
    ):
        """ """

    def fit(self, X, y=None):
        """ """
        self.feature_names_in_ = X.columns.to_numpy()
        self.cortes = {}
        for c in X.columns:
            limites = np.linspace(0, 1, 10 + 1)
            cat_feat = np.char.zfill(
                (X[c].rank(pct=1).values.reshape((-1, 1)) <= limites)
                .argmax(axis=1)
                .astype(str),
                2,
            )

            cat_feat[X[c].isna()] = "00.MISSING"

            self.cortes[c] = dict(
                zip(
                    np.unique(cat_feat),
                    list(
                        zip(
                            X[c].groupby(cat_feat).agg("min"),
                            X[c].groupby(cat_feat).agg("max"),
                        )
                    ),
                )
            )

        return self

    def transform(self, X):
        """ """
        for c in X.columns:
            x_cat = X[c].astype("str").copy()
            lim_ant = np.nan
            for i, (k, v) in enumerate(self.cortes[c].items()):
                if k[:2] == "01":
                    x_cat[(X[c] <= v[1])] = k + ".<=" + str(np.round(v[1], 4))
                    lim_ant = v[1]
                elif i == (len(self.cortes[c]) - 1):
                    x_cat[(X[c] > lim_ant)] = k + ".>" + str(np.round(lim_ant, 4))
                    lim_ant = np.nan
                else:
                    x_cat[(X[c] > lim_ant) & (X[c] <= v[1])] = (
                        k + ".<=" + str(np.round(v[1], 4))
                    )
                    lim_ant = v[1]
            x_cat[X[c].isna()] = "00.MISSING"
            X[c] = x_cat

        return X

    def get_feature_names_out(self, input_features=None):
        check_is_fitted(self)
        if input_features is None:
            input_features = self.feature_names_in_
        return np.array(input_features, dtype=object)
