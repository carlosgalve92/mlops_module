import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted


class mb_clean_text_number(BaseEstimator, TransformerMixin):
    """ """

    def __init__(
        self,
    ):
        """ """

    def fit(self, X, y=None):
        """ """
        self.feature_names_in_ = X.columns.to_numpy()

        return self

    def transform(self, X):
        """ """
        for c in X.columns:
            X[c] = X[c].astype(str).str.replace(r"(\_|,|\")", "", regex=True)
            X[c] = pd.to_numeric(X[c], errors="coerce")
        return X

    def get_feature_names_out(self, input_features=None):
        check_is_fitted(self)
        if input_features is None:
            input_features = self.feature_names_in_
        return np.array(input_features, dtype=object)
